# eops/data/downloader.py
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List
import time
import asyncio
from dataclasses import asdict

from eops.utils.logger import log
from eops.clients import get_client

def _convert_timeframe_to_ms(timeframe: str) -> int:
    """Converts timeframe string to milliseconds."""
    try:
        multipliers = {'m': 60, 'h': 3600, 'd': 86400, 'w': 604800}
        unit = timeframe[-1].lower()
        if unit not in multipliers:
            raise ValueError("Unsupported timeframe unit")
        value = int(timeframe[:-1])
        return value * multipliers[unit] * 1000
    except Exception:
        raise ValueError(f"Invalid timeframe format: '{timeframe}'. Use '1m', '5m', '1h', '4h', '1d', etc.")

async def _fetch_data_for_interval(
    client, 
    instrument_id: str, 
    timeframe: str, 
    start_ts: int, 
    end_ts: int,
    limit: int
) -> List[dict]:
    """
    Fetches all data within a given time interval using a deterministic,
    fixed-step iterative approach.
    """
    all_ohlcv_dict = []
    timeframe_ms = _convert_timeframe_to_ms(timeframe)
    step_ms = limit * timeframe_ms
    
    current_ts = start_ts
    
    log.info(f"Fetching data from {datetime.fromtimestamp(start_ts/1000, tz=timezone.utc)} to {datetime.fromtimestamp(end_ts/1000, tz=timezone.utc)}")
    
    while current_ts < end_ts:
        log.info(f"Fetching window starting from {datetime.fromtimestamp(current_ts/1000, tz=timezone.utc)}...")
        try:
            chunk_of_kline_objects = await client.fetch_klines(
                instrument_id=instrument_id,
                timeframe=timeframe,
                since=current_ts,
                limit=limit
            )
            
            if chunk_of_kline_objects:
                all_ohlcv_dict.extend([asdict(k) for k in chunk_of_kline_objects])
                log.info(f"  -> Fetched {len(chunk_of_kline_objects)} records in this window.")
            else:
                log.info("  -> No data returned for this window, moving to the next.")

        except Exception as e:
            log.error(f"An error occurred during a fetch request: {e}", exc_info=True)
        
        current_ts += step_ms
        await asyncio.sleep(0.5)
    
    return all_ohlcv_dict

def download_ohlcv_data(
    exchange_id: str,
    symbol: str,
    timeframe: str,
    since: str,
    output_path: Path,
    until: Optional[str] = None,
):
    """Downloads historical OHLCV data for a specified date range."""
    try:
        asyncio.run(
            _async_download_ohlcv_data(exchange_id, symbol, timeframe, since, output_path, until)
        )
    except (ValueError, KeyError) as e:
        log.error(e)

async def _async_download_ohlcv_data(
    exchange_id: str,
    symbol: str,
    timeframe: str,
    since: str,
    output_path: Path,
    until: Optional[str] = None,
):
    """The actual async implementation of the data downloader."""
    log.info(f"Attempting to download data for {symbol} on {exchange_id}...")

    client = get_client(exchange_id)
    instrument_id = symbol

    since_ts = int(datetime.strptime(since, '%Y-%m-%d').replace(tzinfo=timezone.utc).timestamp() * 1000)
    until_ts = int(datetime.now(timezone.utc).timestamp() * 1000)
    if until:
        until_ts = int(datetime.strptime(until, '%Y-%m-%d').replace(tzinfo=timezone.utc).timestamp() * 1000)

    limit = 1000
    
    all_ohlcv = await _fetch_data_for_interval(client, instrument_id, timeframe, since_ts, until_ts, limit)

    if not all_ohlcv:
        log.error("Failed to download any data. Please check your parameters.")
        return
        
    log.info(f"Downloaded {len(all_ohlcv)} total data points. Cleaning and saving...")

    df = pd.DataFrame(all_ohlcv)
    df.rename(columns={'timestamp': 'time'}, inplace=True)
    df['time'] = pd.to_datetime(df['time'], unit='ms', utc=True)
    
    df = df.sort_values(by='time').drop_duplicates(subset='time', keep='first')
    
    # --- FIX: Use a pandas-version-compatible way to create timezone-aware datetimes ---
    start_dt = pd.to_datetime(since_ts, unit='ms').tz_localize('UTC')
    end_dt = pd.to_datetime(until_ts, unit='ms').tz_localize('UTC')

    df_filtered = df[(df['time'] >= start_dt) & (df['time'] < end_dt)]
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_filtered.to_csv(output_path, index=False)
    
    log.info(f"💾 Successfully saved {len(df_filtered)} unique data points to: {output_path}")

def fix_ohlcv_data(file_path: Path):
    """Finds and fills gaps in an existing OHLCV data file."""
    try:
        asyncio.run(_async_fix_ohlcv_data(file_path))
    except Exception as e:
        log.error(f"An unexpected error occurred during the fix process: {e}", exc_info=True)

async def _async_fix_ohlcv_data(file_path: Path):
    """The async implementation of the data fixing logic."""
    if not file_path.exists():
        log.error(f"File not found: {file_path}")
        return

    filename = file_path.stem
    parts = filename.split('_')
    if len(parts) < 3:
        log.error(f"Filename '{filename}' does not match 'exchange_symbol_timeframe' format.")
        return
        
    exchange_id = parts[0]
    timeframe = parts[-1]
    symbol = "_".join(parts[1:-1])
    
    log.info(f"Starting data fix for {file_path}")
    log.info(f"  - Exchange: {exchange_id}, Symbol: {symbol}, Timeframe: {timeframe}")

    try:
        df = pd.read_csv(file_path, parse_dates=['time'])
        if df.empty:
            log.warning("File is empty. Cannot perform a fix.")
            return
        # Ensure the loaded time column is timezone-aware
        if df['time'].dt.tz is None:
            df['time'] = df['time'].dt.tz_localize('UTC')
        df = df.drop_duplicates(subset=['time']).set_index('time').sort_index()
        log.info(f"Loaded {len(df)} existing data points from {df.index.min().date()} to {df.index.max().date()}.")
    except Exception as e:
        log.error(f"Failed to load or parse CSV file: {e}")
        return

    try:
        timeframe_freq = timeframe.replace('h', 'H').replace('d', 'D').replace('m', 'T')
        full_index = pd.date_range(start=df.index.min(), end=df.index.max(), freq=timeframe_freq, tz='UTC')
    except ValueError as e:
        log.error(f"Could not determine frequency from timeframe '{timeframe}'. Error: {e}")
        return
    
    missing_timestamps = full_index.difference(df.index)
    
    if missing_timestamps.empty:
        log.info("✅ No gaps found in the data.")
        return
        
    log.warning(f"Found {len(missing_timestamps)} missing timestamps.")

    gaps = []
    if not missing_timestamps.empty:
        missing_series = missing_timestamps.to_series()
        expected_freq = pd.to_timedelta(timeframe.replace('h', 'H'))
        breaks = missing_series.diff() != expected_freq
        groups = breaks.cumsum()
        for _, group in missing_series.groupby(groups):
            gaps.append((group.min(), group.max()))

    log.info(f"Identified {len(gaps)} gaps to fill.")

    client = get_client(exchange_id)
    instrument_id = symbol
    limit = 1000

    new_data = []
    for i, (start_gap, end_gap) in enumerate(gaps, 1):
        log.info(f"--- Fixing gap {i}/{len(gaps)}: from {start_gap.strftime('%Y-%m-%d %H:%M')} to {end_gap.strftime('%Y-%m-%d %H:%M')} ---")
        
        start_ts = int(start_gap.timestamp() * 1000)
        end_ts = int(end_gap.timestamp() * 1000) + _convert_timeframe_to_ms(timeframe)
        
        chunk = await _fetch_data_for_interval(client, instrument_id, timeframe, start_ts, end_ts, limit)
        if chunk:
            log.info(f"Fetched {len(chunk)} new data points for this gap.")
            new_data.extend(chunk)

    if not new_data:
        log.warning("Could not fetch any new data to fill gaps.")
        return

    new_df = pd.DataFrame(new_data)
    if not new_df.empty:
        new_df.rename(columns={'timestamp': 'time'}, inplace=True)
        new_df['time'] = pd.to_datetime(new_df['time'], unit='ms', utc=True)
    
    combined_df = pd.concat([df.reset_index(), new_df])
    final_df = combined_df.sort_values(by='time').drop_duplicates(subset='time', keep='first')
    
    final_df.to_csv(file_path, index=False)
    log.info(f"💾 Successfully fixed data. Total data points now: {len(final_df)}. Saved to {file_path}")