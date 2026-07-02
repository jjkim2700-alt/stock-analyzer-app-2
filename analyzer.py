import pandas as pd
import numpy as np

def calculate_sma(df: pd.DataFrame, windows=[20, 60, 120]) -> pd.DataFrame:
    """이동평균선(SMA)을 계산합니다."""
    for window in windows:
        df[f'SMA_{window}'] = df['Close'].rolling(window=window).mean()
    return df

def calculate_rsi(df: pd.DataFrame, window=14) -> pd.DataFrame:
    """RSI(상대강도지수)를 계산합니다."""
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df

def calculate_macd(df: pd.DataFrame) -> pd.DataFrame:
    """MACD를 계산합니다."""
    short_ema = df['Close'].ewm(span=12, adjust=False).mean()
    long_ema = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = short_ema - long_ema
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
    return df

def calculate_bollinger_bands(df: pd.DataFrame, window=20) -> pd.DataFrame:
    """볼린저 밴드를 계산합니다."""
    sma = df['Close'].rolling(window=window).mean()
    std = df['Close'].rolling(window=window).std()
    df['BB_Upper'] = sma + (std * 2)
    df['BB_Lower'] = sma - (std * 2)
    df['BB_Middle'] = sma
    return df

def get_trading_signal(df: pd.DataFrame) -> str:
    """RSI 기반 매수/매도 신호를 생성합니다."""
    if df.empty or 'RSI' not in df.columns:
        return "데이터 없음"
    
    latest_rsi = df['RSI'].iloc[-1]
    
    if latest_rsi <= 30:
        return "과매도 (매수 검토 권장)"
    elif latest_rsi >= 70:
        return "과매수 (매도 검토 권장)"
    else:
        return "중립 (추세 관망)"

def generate_detailed_report(df: pd.DataFrame) -> str:
    """지표를 종합하여 한글 분석 의견을 생성합니다."""
    if df.empty: return "분석할 데이터가 없습니다."
    
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    reports = []
    
    # 1. 추세 분석 (이동평균선)
    if latest['Close'] > latest['SMA_20'] > latest['SMA_60']:
        reports.append("✅ **추세:** 현재 주가가 단기 및 중기 이동평균선 위에 위치하여 강한 상승 추세를 유지하고 있습니다.")
    elif latest['Close'] < latest['SMA_20'] < latest['SMA_60']:
        reports.append("⚠️ **추세:** 주가가 이동평균선 아래로 하향 돌파하며 하락 압력이 강해지고 있는 모습입니다.")
    else:
        reports.append("ℹ️ **추세:** 현재 주가가 이동평균선 부근에서 혼조세를 보이며 방향성을 탐색 중입니다.")
        
    # 2. 과열 및 바닥 분석 (RSI)
    if latest['RSI'] >= 70:
        reports.append(f"🔴 **심리:** RSI 지수가 {latest['RSI']:.1f}로 과매수 구간에 진입했습니다. 단기 조정 가능성에 유의하며 분할 매도를 검토할 시점입니다.")
    elif latest['RSI'] <= 30:
        reports.append(f"🟢 **심리:** RSI 지수가 {latest['RSI']:.1f}로 과매도 구간입니다. 가격 메리트가 발생한 지점으로 반등을 기대하며 분할 매수를 고려해 볼 수 있습니다.")
    else:
        reports.append(f"⚪ **심리:** RSI 지수가 {latest['RSI']:.1f}로 안정적인 흐름입니다. 특별한 과열이나 침체 징후는 보이지 않습니다.")
        
    # 3. 변동성 분석 (볼린저 밴드)
    if latest['Close'] >= latest['BB_Upper']:
        reports.append("📉 **변동성:** 주가가 볼린저 밴드 상단을 터치했습니다. 통계적으로 밴드 안으로 회귀하려는 성질이 있어 일시적 눌림목이 발생할 수 있습니다.")
    elif latest['Close'] <= latest['BB_Lower']:
        reports.append("📈 **변동성:** 주가가 볼린저 밴드 하단에 도달했습니다. 과도한 하락에 따른 기술적 반등이 기대되는 자리입니다.")
        
    # 4. 모멘텀 분석 (MACD)
    if latest['MACD'] > latest['MACD_Signal'] and prev['MACD'] <= prev['MACD_Signal']:
        reports.append("🚀 **모멘텀:** MACD 골든크로스가 발생했습니다! 상승 동력이 강화되고 있는 긍정적인 신호입니다.")
    elif latest['MACD'] < latest['MACD_Signal'] and prev['MACD'] >= prev['MACD_Signal']:
        reports.append("🥀 **모멘텀:** MACD 데드크로스가 발생했습니다. 하락 추세로의 전환 가능성이 있으니 주의가 필요합니다.")

    return "\n\n".join(reports)

def calculate_signals(df: pd.DataFrame) -> pd.DataFrame:
    """차트에 표시할 매수/매도 시그널 지점을 계산합니다."""
    # 매수 신호: RSI 30 이하 근접 + MACD 골든크로스
    df['Buy_Signal'] = (df['RSI'] <= 35) & \
                      (df['MACD'] > df['MACD_Signal']) & \
                      (df['MACD'].shift(1) <= df['MACD_Signal'].shift(1))
    
    # 매도 신호: RSI 70 이상 근접 + MACD 데드크로스
    df['Sell_Signal'] = (df['RSI'] >= 65) & \
                       (df['MACD'] < df['MACD_Signal']) & \
                       (df['MACD'].shift(1) >= df['MACD_Signal'].shift(1))
    return df

def run_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """모든 기술적 지표 및 시그널을 한 번에 계산합니다."""
    df = calculate_sma(df)
    df = calculate_rsi(df)
    df = calculate_macd(df)
    df = calculate_bollinger_bands(df)
    df = calculate_signals(df)
    return df
