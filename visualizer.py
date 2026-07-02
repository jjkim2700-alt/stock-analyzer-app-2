import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def create_stock_chart(df: pd.DataFrame, ticker: str):
    """
    캔들스틱, 이동평균선, 볼린저 밴드, RSI, MACD를 포함한 통합 차트를 생성합니다.
    """
    # 서브플롯 생성: 3행 1열 (메인차트, RSI, MACD)
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.6, 0.2, 0.2],
        subplot_titles=(f'{ticker}', 'RSI', 'MACD')
    )

    # 1. 메인 차트: 캔들스틱
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Candlestick'
        ),
        row=1, col=1
    )

    # 이동평균선 추가
    for col in ['SMA_20', 'SMA_60', 'SMA_120']:
        if col in df.columns:
            fig.add_trace(
                go.Scatter(x=df.index, y=df[col], name=col, line=dict(width=1.5)),
                row=1, col=1
            )

    # 볼린저 밴드 추가
    if 'BB_Upper' in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df['BB_Upper'], 
                name='BB Upper', 
                line=dict(color='rgba(173, 216, 230, 0.4)', dash='dash')
            ),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df['BB_Lower'], 
                name='BB Lower', 
                line=dict(color='rgba(173, 216, 230, 0.4)', dash='dash'),
                fill='tonexty' # 상한선과 하한선 사이 채우기
            ),
            row=1, col=1
        )

    # 4. 매수/매도 시그널 마커 추가
    # 매수 신호 (초록색 위 화살표)
    buy_indices = df[df['Buy_Signal']].index
    if not buy_indices.empty:
        fig.add_trace(
            go.Scatter(
                x=buy_indices, 
                y=df.loc[buy_indices, 'Low'] * 0.98, # 저가보다 약간 아래 표시
                mode='markers',
                marker=dict(symbol='triangle-up', size=15, color='#00ff00', line=dict(width=2, color='white')),
                name='Buy Signal'
            ),
            row=1, col=1
        )

    # 매도 신호 (빨간색 아래 화살표)
    sell_indices = df[df['Sell_Signal']].index
    if not sell_indices.empty:
        fig.add_trace(
            go.Scatter(
                x=sell_indices, 
                y=df.loc[sell_indices, 'High'] * 1.02, # 고가보다 약간 위 표시
                mode='markers',
                marker=dict(symbol='triangle-down', size=15, color='#ff0000', line=dict(width=2, color='white')),
                name='Sell Signal'
            ),
            row=1, col=1
        )

    # 2. RSI 차트
    if 'RSI' in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='purple')),
            row=2, col=1
        )
        # 기준선 (30, 70)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

    # 3. MACD 차트
    if 'MACD' in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df['MACD'], name='MACD', line=dict(color='blue')),
            row=3, col=1
        )
        fig.add_trace(
            go.Scatter(x=df.index, y=df['MACD_Signal'], name='Signal', line=dict(color='orange')),
            row=3, col=1
        )
        fig.add_trace(
            go.Bar(x=df.index, y=df['MACD_Hist'], name='Histogram'),
            row=3, col=1
        )

    # 레이아웃 설정 (모바일 반응형)
    fig.update_layout(
        height=700,
        autosize=True,
        xaxis_rangeslider_visible=False,
        showlegend=True,
        legend=dict(
            orientation='h',       # 범례 가로 배치 (모바일 공간 확보)
            yanchor='bottom',
            y=-0.15,
            xanchor='center',
            x=0.5,
            font=dict(size=10)
        ),
        template='plotly_dark',
        margin=dict(l=10, r=10, t=40, b=10),  # 모바일 마진 최소화
        font=dict(size=10),
    )
    # 축 레이블 크기 조정
    fig.update_xaxes(tickfont=dict(size=9))
    fig.update_yaxes(tickfont=dict(size=9))

    return fig
