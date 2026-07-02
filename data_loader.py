import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def fetch_stock_data(ticker: str, period: str = "1y") -> pd.DataFrame:
    """
    주어진 티커에 대한 주가 데이터를 가져옵니다.
    
    Args:
        ticker (str): 종목 티커 (예: 'AAPL', '005930.KS')
        period (str): 데이터 기간 (기본값: '1y')
        
    Returns:
        pd.DataFrame: 주가 데이터프레임
    """
    try:
        # 데이터 수집
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        
        if df.empty:
            raise ValueError(f"티커 '{ticker}'에 대한 데이터를 찾을 수 없습니다.")
            
        return df
    except Exception as e:
        print(f"데이터 수집 중 오류 발생: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    # 테스트 코드
    test_df = fetch_stock_data("005930.KS") # 삼성전자
    print(test_df.head())
