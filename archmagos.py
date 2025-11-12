import pandas as pd
import logging
import os
from datetime import datetime
from rich.table import Table
from rich import print as rich_print

def archmagos_forge_signal(df: pd.DataFrame, analysis: dict, symbol: str) -> dict | None:
    """
    The Archmagos reviews the Tech-Priest's analysis and forges a
    Primaris-Signal if and only if all conditions of the sacred doctrine are met.
    If a signal is found, it is recorded in a text file.
    """
    logging.info(f"Archmagos reviewing analysis for {symbol}...")

    # --- Debug Printout using Rich Table ---
    try:
        table = Table(title=f"--- Essential Data for {symbol} ---", border_style="blue")
        essential_cols = ['close', 'RSI_9', 'BBL_20_2.0_2.0', 'BBU_20_2.0_2.0', 'STOCHRSIk_14_9_3_3', 'STOCHRSId_14_9_3_3']
        df_tail = df[essential_cols].tail(5)

        for col in df_tail.columns:
            table.add_column(col, justify="right")

        for index, row in df_tail.iterrows():
            row_values = []
            for col_name, value in row.items():
                style = ""
                if col_name == 'RSI_9':
                    if value > 70: style = "bold red"
                    elif value < 30: style = "bold green"
                elif col_name.startswith('STOCHRSI'):
                    if value > 80: style = "bold red"
                    elif value < 20: style = "bold green"
                
                if style:
                    row_values.append(f"[{style}]{value:.2f}[/{style}]")
                else:
                    row_values.append(f"{value:.2f}")
            table.add_row(*row_values)
        
        rich_print(table)

    except KeyError as e:
        logging.error(f"Debug Error: A column is missing from the DataFrame - {e}")
        logging.error(f"Available columns: {df.columns.tolist()}")
    # --- End Debug Printout ---

    # Retrieve the last two data points for crossover detection
    last = df.iloc[-1]
    prev = df.iloc[-2]

    # --- Sacred Doctrine: Define LONG Entry Conditions ---
    long_signal_conditions = (
        last['RSI_9'] < 30 and
        last['close'] <= last['BBL_20_2.0_2.0'] and
        # StochRSI bullish crossover check in oversold zone
        last['STOCHRSIk_14_9_3_3'] < 20 and
        last['STOCHRSIk_14_9_3_3'] > last['STOCHRSId_14_9_3_3'] and
        prev['STOCHRSIk_14_9_3_3'] <= prev['STOCHRSId_14_9_3_3']
    )

    # --- Sacred Doctrine: Define SHORT Entry Conditions ---
    short_signal_conditions = (
        last['RSI_9'] > 70 and
        last['close'] >= last['BBU_20_2.0_2.0'] and
        # StochRSI bearish crossover check in overbought zone
        last['STOCHRSIk_14_9_3_3'] > 80 and
        last['STOCHRSIk_14_9_3_3'] < last['STOCHRSId_14_9_3_3'] and
        prev['STOCHRSIk_14_9_3_3'] >= prev['STOCHRSId_14_9_3_3']
    )

    signal_type = None
    bollinger_band = None

    if long_signal_conditions:
        signal_type = "LONG_REVERSAL"
        bollinger_band = "LOWER"
        logging.warning(f"WORTHY LONG SIGNAL DETECTED FOR {symbol}! Forging Primaris-Signal...")
    elif short_signal_conditions:
        signal_type = "SHORT_REVERSAL"
        bollinger_band = "UPPER"
        logging.warning(f"WORTHY SHORT SIGNAL DETECTED FOR {symbol}! Forging Primaris-Signal...")
    else:
        logging.info(f"No signal found for {symbol}. Conditions not met.")
        return None

    # A worthy signal has been found. Forge the Primaris-Signal.
    signal = {
        "symbol": symbol,
        "timestamp": df.index[-1].isoformat(),
        "trend_assessment": analysis['trend'],
        "signal_type": signal_type,
        "key_indicators": {
            "rsi": round(last['RSI_9'], 2),
            "stoch_rsi_k": round(last['STOCHRSIk_14_9_3_3'], 2),
            "stoch_rsi_d": round(last['STOCHRSId_14_9_3_3'], 2),
            "bollinger_band": bollinger_band,
            "volume_spike": bool(analysis['volume_spike'])
        },
        "suggested_volatility_profile": analysis['volatility']
    }
    
    # --- Record the signal ---
    try:
        signals_dir = 'signals'
        os.makedirs(signals_dir, exist_ok=True)
        
        date_str = datetime.now().strftime('%Y-%m-%d')
        file_path = os.path.join(signals_dir, f"{date_str}_Primaris_Signal.txt")
        
        signal_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        signal_entry = f"--- Signal Found at {signal_time} for {signal['symbol']} ---"
        signal_entry += f"Timestamp: {signal['timestamp']}"
        signal_entry += f"Type: {signal['signal_type']}"
        signal_entry += f"Trend Assessment: {signal['trend_assessment']}"
        signal_entry += "Key Indicators:\n"
        for key, value in signal['key_indicators'].items():
            signal_entry += f"  - {key}: {value}\n"
        signal_entry += f"Suggested Volatility Profile: {signal['suggested_volatility_profile']}\n"
        signal_entry += "---\n\n"

        with open(file_path, 'a') as f:
            f.write(signal_entry)
        logging.info(f"Successfully wrote signal to {file_path}")

    except Exception as e:
        logging.error(f"Error writing signal to file: {e}")

    return signal