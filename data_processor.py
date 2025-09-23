import pandas as pd
import pandas_ta as ta
import logging

def determine_trend(df: pd.DataFrame, fast_ma: int = 12, slow_ma: int = 26, sideways_threshold: float = 0.5) -> str:
    """A litany to discern the market's primary trend or sideways movement."""
    df['fast_ma'] = df['close'].rolling(window=fast_ma).mean()
    df['slow_ma'] = df['close'].rolling(window=slow_ma).mean()
    
    # Calculate the percentage difference between fast and slow MA
    ma_diff_pct = abs((df['fast_ma'].iloc[-1] - df['slow_ma'].iloc[-1]) / df['slow_ma'].iloc[-1]) * 100
    
    logging.info(f"Fast MA: {df['fast_ma'].iloc[-1]:.2f}, Slow MA: {df['slow_ma'].iloc[-1]:.2f}")  # Debugging output
    logging.info(f"MA Difference Percentage: {ma_diff_pct:.2f}%")  # Debugging output
    # Check for sideways market: MAs are close together
    if ma_diff_pct <= sideways_threshold:
        return "SIDEWAYS"
    elif df['fast_ma'].iloc[-1] > df['slow_ma'].iloc[-1]:
        return "UPTREND"
    else:
        return "DOWNTREND"

def determine_volatility(df: pd.DataFrame) -> str:
    """A canticle to gauge the market's chaotic energy (volatility)."""
    # ATRr is calculated as a percentage
    atr_percentage = df['ATRr_10'].iloc[-1]
    if atr_percentage > 3.0:
        return "HIGH"
    if atr_percentage > 1.0:
        return "MODERATE"
    return "LOW"

def _check_for_volume_spike(df: pd.DataFrame, multiplier: float = 2.0) -> bool:
    """A rite to confirm the strength of the machine spirit's conviction (volume)."""
    df['volume_ma'] = df['volume'].rolling(window=20).mean()
    return df['volume'].iloc[-1] > (df['volume_ma'].iloc[-1] * multiplier)

def tech_priest_analyze_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    The Tech-Priest applies sacred analytical rites to the raw data.
    It calculates all necessary indicators and higher-order truths.
    """
    logging.info("Tech-Priest beginning analytical rites...")

    # Calculate all necessary indicators directly
    df.ta.rsi(length=9, append=True)
    df.ta.stochrsi(length=14, rsi_length=9, k=3, d=3, append=True)
    df.ta.bbands(length=20, append=True)
    df.ta.atr(length=10, mamode="rma", append=True)

    # Discern higher-order truths from the indicators
    analysis = {
        "trend": determine_trend(df),
        "volatility": determine_volatility(df),
        "volume_spike": _check_for_volume_spike(df)
    }

    logging.info(f"Analysis complete. Trend: {analysis['trend']}, Volatility: {analysis['volatility']}.")
    return df, analysis