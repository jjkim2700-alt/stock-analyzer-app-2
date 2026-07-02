import streamlit as st
import pandas as pd
from data_loader import fetch_stock_data
from analyzer import run_analysis, get_trading_signal, generate_detailed_report
from visualizer import create_stock_chart
import base64

# 페이지 설정
st.set_page_config(
    page_title="Stock Analysis Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS (Premium Design)
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background: linear-gradient(145deg, #1e2130, #11141d);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #3d4156;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    /* 지표 텍스트 색상 강제 지정 */
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetricLabel"] {
        color: #a0a0a0 !important;
        font-size: 0.9rem !important;
    }
    [data-testid="stMetricDelta"] {
        font-size: 0.9rem !important;
    }
    .signal-box {
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        font-size: 1.2rem;
        margin-bottom: 20px;
    }
    .buy-signal { background-color: rgba(0, 255, 0, 0.1); border: 2px solid #00ff00; color: #00ff00; }
    .sell-signal { background-color: rgba(255, 0, 0, 0.1); border: 2px solid #ff0000; color: #ff0000; }
    .neutral-signal { background-color: rgba(255, 255, 255, 0.1); border: 2px solid #ffffff; color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

def main():
    # 세션 상태 초기화 (버튼 클릭 시 종목 변경 및 분석 실행을 위함)
    if 'ticker_input' not in st.session_state:
        st.session_state.ticker_input = "AAPL"
    if 'do_analysis' not in st.session_state:
        st.session_state.do_analysis = False

    st.sidebar.title("🚀 Stock Analyzer Settings")
    st.sidebar.markdown("---")

    # ── 🇰🇷 한국 주요 종목 드롭다운 ──
    st.sidebar.subheader("🇰🇷 한국 주요 종목")

    KR_STOCKS = {
        "── 선택하세요 ──": "",
        "📦 반도체·IT": {
            "삼성전자 (005930)":       "005930.KS",
            "SK하이닉스 (000660)":     "000660.KS",
            "삼성전자우 (005935)":     "005935.KS",
            "NAVER (035420)":          "035420.KS",
            "카카오 (035720)":         "035720.KS",
        },
        "🚗 자동차·모빌리티": {
            "현대차 (005380)":         "005380.KS",
            "기아 (000270)":           "000270.KS",
            "현대모비스 (012330)":     "012330.KS",
        },
        "🔋 이차전지·배터리": {
            "LG에너지솔루션 (373220)": "373220.KS",
            "삼성SDI (006400)":        "006400.KS",
            "포스코퓨처엠 (003670)":   "003670.KS",
            "에코프로비엠 (247540)":   "247540.KQ",
        },
        "💊 바이오·제약": {
            "삼성바이오로직스 (207940)":"207940.KS",
            "셀트리온 (068270)":        "068270.KS",
        },
        "🏭 지주·제조·방산": {
            "삼성물산 (028260)":        "028260.KS",
            "한화에어로스페이스 (012450)": "012450.KS",
            "LG화학 (051910)":          "051910.KS",
        },
        "🏦 금융": {
            "KB금융 (105560)":          "105560.KS",
            "신한지주 (055550)":        "055550.KS",
        },
    }

    # 카테고리 선택
    categories = list(KR_STOCKS.keys())
    selected_cat = st.sidebar.selectbox("카테고리", categories, index=0)

    # 종목 선택 (카테고리가 선택된 경우)
    if selected_cat != "── 선택하세요 ──" and isinstance(KR_STOCKS[selected_cat], dict):
        stock_options = ["── 종목 선택 ──"] + list(KR_STOCKS[selected_cat].keys())
        selected_stock = st.sidebar.selectbox("종목", stock_options, index=0)

        if selected_stock != "── 종목 선택 ──":
            symbol = KR_STOCKS[selected_cat][selected_stock]
            if st.sidebar.button(f"📊 {selected_stock} 분석", use_container_width=True):
                st.session_state.ticker_input = symbol
                st.session_state.do_analysis = True

    st.sidebar.markdown("---")

    # 🔥 Hot Stocks 섹션
    st.sidebar.subheader("🔥 Hot Stocks (Quick)")

    hot_stocks = {
        "🇺🇸 USA": {"NVDA": "NVIDIA", "TSLA": "Tesla", "AAPL": "Apple"},
        "🇰🇷 KOREA": {"005930.KS": "삼성전자", "000660.KS": "SK하이닉스", "247540.KQ": "에코프로비엠"},
        "🇨🇳 CHINA": {"600519.SS": "귀주모태주", "002594.SZ": "BYD", "300750.SZ": "CATL"}
    }

    for country, stocks in hot_stocks.items():
        st.sidebar.write(f"**{country}**")
        cols = st.sidebar.columns(3)
        for i, (symbol, name) in enumerate(stocks.items()):
            if cols[i%3].button(symbol, help=name):
                st.session_state.ticker_input = symbol
                st.session_state.do_analysis = True
        st.sidebar.markdown("")

    st.sidebar.markdown("---")

    # 직접 입력
    ticker = st.sidebar.text_input(
        "직접 입력 (예: AAPL, 005930.KS)",
        value=st.session_state.ticker_input,
        key="ticker_field"
    )
    period = st.sidebar.selectbox("분석 기간", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)

    # 분석 시작 버튼 (수동)
    manual_analysis = st.sidebar.button("▶ 분석 시작", use_container_width=True)
    
    st.title("📈 Stock Investment Assistant Pro")
    
    # 분석 실행 조건 (수동 버튼 클릭 또는 핫 스탁 버튼 클릭 시)
    if manual_analysis or st.session_state.do_analysis:
        st.session_state.do_analysis = False # 플래그 초기화
        # 수동 입력값이 있을 경우 세션 상태 업데이트
        current_ticker = st.session_state.ticker_field if manual_analysis else st.session_state.ticker_input
        
        st.markdown(f"**현재 분석 종목:** `{current_ticker}` | **분석 기간:** `{period}`")
        with st.spinner("데이터를 불러오고 분석 중입니다..."):
            # 1. 데이터 수집
            df = fetch_stock_data(current_ticker, period)
            
            if not df.empty:
                # 2. 분석 수행
                df = run_analysis(df)
                
                # 3. 주요 지표 표시 (Metrics)
                col1, col2, col3, col4 = st.columns(4)
                latest = df.iloc[-1]
                prev = df.iloc[-2]
                
                change = latest['Close'] - prev['Close']
                pct_change = (change / prev['Close']) * 100
                
                col1.metric("현재가", f"{latest['Close']:.2f}", f"{change:.2f} ({pct_change:.2f}%)")
                col2.metric("고가 (Day)", f"{latest['High']:.2f}")
                col3.metric("저가 (Day)", f"{latest['Low']:.2f}")
                col4.metric("RSI (14)", f"{latest['RSI']:.2f}")
                
                # 4. 투자 전략 알림
                signal = get_trading_signal(df)
                signal_class = "neutral-signal"
                if "매수" in signal: signal_class = "buy-signal"
                elif "매도" in signal: signal_class = "sell-signal"
                
                st.markdown(f'<div class="signal-box {signal_class}">투자 전략 신호: {signal}</div>', unsafe_allow_html=True)
                
                # 4-1. 상세 AI 분석 리포트 추가
                with st.expander("🤖 AI 상세 분석 의견 보기 (클릭)", expanded=True):
                    report = generate_detailed_report(df)
                    st.markdown(report)
                
                # 5. 차트 시각화
                fig = create_stock_chart(df, current_ticker)
                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config={
                        'responsive': True,
                        'displayModeBar': False,   # 모바일에서 툴바 숨김 (화면 공간 확보)
                        'scrollZoom': False,
                    }
                )
                
                # 6. 데이터 테이블 및 다운로드
                st.subheader("📋 분석 데이터 리스트")
                st.dataframe(df.tail(20).style.format("{:.2f}"))
                
                # CSV 다운로드
                csv = df.to_csv().encode('utf-8')
                st.download_button(
                    label="CSV 파일 내보내기",
                    data=csv,
                    file_name=f"{current_ticker}_analysis_{period}.csv",
                    mime="text/csv",
                )
            else:
                st.error("데이터를 불러오지 못했습니다. 티커를 확인해 주세요.")
    else:
        st.info("왼쪽 사이드바에서 티커를 입력하고 '분석 시작' 버튼을 눌러주세요.")

if __name__ == "__main__":
    main()
