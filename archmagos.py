
import pandas as pd
import logging

def archmagos_forge_signal(df: pd.DataFrame, analysis: dict, symbol: str) -> dict | None:
    """
    The Archmagos reviews the Tech-Priest's analysis and forges a
    Primaris-Signal if and only if all conditions of the sacred doctrine are met.
    """
    logging.info(f"Archmagos reviewing analysis for {symbol}...")

    # Print essential columns for debugging
    try:
        essential_cols = ['close', 'RSI_9', 'BBL_20_2.0_2.0', 'BBU_20_2.0_2.0', 'STOCHRSIk_14_9_3_3', 'STOCHRSId_14_9_3_3']
        print(f"--- Essential Data for {symbol} ---")
        print(df[essential_cols].tail(5))
        print("-------------------------------------")
    except KeyError as e:
        print(f"Debug Error: A column is missing from the DataFrame - {e}")
        print("Available columns:", df.columns.tolist())

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
            "volume_spike": analysis['volume_spike']
        },
        "suggested_volatility_profile": analysis['volatility']
    }
    
    return signal
