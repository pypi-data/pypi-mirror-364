# eops/worker.py
"""
The operational entrypoint for managing strategy instances.
It receives a final configuration dictionary and runs the engine.
"""
import typer
import json
import os
import signal
from pathlib import Path
from multiprocessing import Process, current_process
from typing import Dict, Any

import sys
# It's better to manage path in the caller (dashboard), but keep this for standalone use
sys.path.insert(0, str(Path(__file__).parent.parent))

from eops.core.engine import Engine
# from eops.utils.config_loader import load_config_from_dict # No longer used
from eops.utils.logger import setup_logger

app = typer.Typer(help="Eops Worker: Runs a single strategy instance from a config.")
log = setup_logger("worker")

def run_eops_instance(instance_id: str, config_dict: Dict[str, Any]):
    """
    This function is the target for the new process. It sets up and runs a single
    eops Engine instance from a complete configuration dictionary.
    """
    current_process().name = f"eops-inst-{instance_id}"
    
    # The config dict should already contain the log file path if needed
    log_file = config_dict.get('LOG_FILE')
    instance_log = setup_logger(instance_id, log_file=Path(log_file) if log_file else None)
    
    try:
        instance_log.info(f"Process {os.getpid()} starting up for instance.")
        
        # Add project root to sys.path if specified in config
        # This is crucial for the engine to import the strategy class
        project_root = config_dict.get("PROJECT_ROOT")
        if project_root and project_root not in sys.path:
            sys.path.insert(0, project_root)

        # The config_dict is now the final, complete configuration
        engine = Engine(config_dict)
        
        # The engine's run method blocks until a SIGTERM is received.
        # It's an async function, so we need to run it in an event loop.
        import asyncio
        asyncio.run(engine.run())

    except Exception as e:
        instance_log.error(f"FATAL ERROR in instance process: {e}", exc_info=True)
    finally:
        instance_log.info(f"Process {os.getpid()} for instance is shutting down.")

@app.command()
def start(
    instance_id: str = typer.Argument(..., help="A unique UUID for the strategy instance."),
    config_json: str = typer.Argument(..., help="A JSON string containing the final strategy configuration."),
):
    """
    Starts a new strategy instance as a OS process from a JSON config string.
    This is the main entrypoint for the dashboard orchestrator.
    """
    log.info(f"Received 'start' command for instance: {instance_id}")

    try:
        config = json.loads(config_json)
        # We need to deserialize the strategy class string back into a class object
        module_path, class_name = config["STRATEGY_CLASS"].rsplit('.', 1)
        module = __import__(module_path, fromlist=[class_name])
        config["STRATEGY_CLASS"] = getattr(module, class_name)
    except (json.JSONDecodeError, KeyError, ImportError) as e:
        log.error(f"Invalid or incomplete configuration JSON for instance '{instance_id}': {e}")
        raise typer.Exit(code=1)

    # This is now a blocking call, not creating a background process itself.
    # The dashboard will run this command in a subprocess.
    run_eops_instance(instance_id, config)
    
    log.info(f"✅ Instance '{instance_id}' process finished.")
    typer.echo(f"OK: Instance {instance_id} finished.")


if __name__ == "__main__":
    app()