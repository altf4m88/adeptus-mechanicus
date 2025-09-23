import os
import math
import logging
from dotenv import load_dotenv
from pybit.unified_trading import HTTP
import pandas as pd

load_dotenv()

session = HTTP(
    testnet=False,
    demo=True,
    api_key=os.environ.get("BYBIT_API_KEY_TESTNET"),
    api_secret=os.environ.get("BYBIT_API_SECRET_TESTNET"),
    timeout=30,
)

def get_top_volume_symbols(limit: int = 50) -> list[str]:
    """
    Fetches tickers for perpetual futures, sorts them by 24h volume,
    and returns the top symbols.
    """
    try:
        response = session.get_tickers(category="linear")
        if response['retCode'] == 0 and 'list' in response['result']:
            tickers = response['result']['list']
            
            # Filter for USDT perpetuals and sort by 24h volume
            usdt_tickers = [t for t in tickers if t['symbol'].endswith('USDT')]
            sorted_tickers = sorted(usdt_tickers, key=lambda x: float(x.get('turnover24h', 0)), reverse=True)
            
            # Get the top symbols
            top_symbols = [t['symbol'] for t in sorted_tickers[:limit]]
            logging.info(f"Servitor identified top {len(top_symbols)} symbols by volume.")
            return top_symbols
        else:
            logging.error(f"Error fetching tickers: {response.get('retMsg', 'Unknown error')}")
            return []
    except Exception as e:
        logging.error(f"An exception occurred while fetching top volume symbols: {e}")
        return []

def servitor_fetch_market_data(symbol: str, interval: int = 15, limit: int = 200) -> pd.DataFrame | None:
    """
    The Servitor's sole function is to retrieve raw market data from the
    Noosphere (Bybit API).
    """
    try:
        logging.info(f"Servitor dispatched to fetch data for {symbol} on {interval}m interval.")
        response = session.get_kline(
            category="linear",
            symbol=symbol,
            interval=interval,
            limit=limit
        )

        if response['retCode'] == 0 and 'list' in response['result']:
            data = response['result']['list']
            df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume", "turnover"])
            
            df['timestamp'] = pd.to_datetime(pd.to_numeric(df['timestamp']), unit='ms')
            df.set_index('timestamp', inplace=True)
            
            numeric_columns = ["open", "high", "low", "close", "volume", "turnover"]
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            df.sort_index(ascending=True, inplace=True)
            
            logging.info(f"Servitor returned with {len(df)} data points for {symbol}.")
            return df
        else:
            logging.error(f"Servitor failed to fetch data for {symbol}: {response.get('retMsg')}")
            return None
    except Exception as e:
        logging.error(f"A critical error occurred in the Servitor unit: {e}")
        return None

def safe_float_convert(value, default=0.0):
    """
    Safely convert a value to float, handling empty strings and None values.
    """
    if value is None or value == '' or value == 'null':
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default