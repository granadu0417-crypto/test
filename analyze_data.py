"""
바이낸스 BTCUSDT 1분봉 데이터 분석 프로그램
- 1년치 데이터의 특성을 파악합니다
- 변동성, 패턴 등을 분석하여 전략 수립에 활용합니다
"""

import pandas as pd
import numpy as np
from pathlib import Path
import glob

print("=" * 80)
print("📊 BTCUSDT 1분봉 데이터 분석 시작")
print("=" * 80)
print()

# 1단계: 데이터 파일 찾기
print("1️⃣ 데이터 파일 로딩 중...")
data_path = Path("data/futures/um/monthly/klines/BTCUSDT/1m")
csv_files = sorted(glob.glob(str(data_path / "*.csv")))

print(f"   찾은 파일 개수: {len(csv_files)}개")
for f in csv_files:
    print(f"   - {Path(f).name}")
print()

# 2단계: 모든 데이터 합치기
print("2️⃣ 데이터 병합 중...")

# CSV 컬럼명 정의 (바이낸스 선물 klines 형식)
columns = [
    'open_time',      # 시작 시간
    'open',           # 시가
    'high',           # 고가
    'low',            # 저가
    'close',          # 종가
    'volume',         # 거래량
    'close_time',     # 종료 시간
    'quote_volume',   # Quote 거래량
    'trades',         # 거래 횟수
    'taker_buy_base', # 테이커 매수 거래량
    'taker_buy_quote',# 테이커 매수 Quote 거래량
    'ignore'          # 무시
]

# 모든 CSV 파일 읽어서 합치기
dfs = []
for csv_file in csv_files:
    df = pd.read_csv(csv_file, names=columns)
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

# 시간을 datetime으로 변환
df_all['timestamp'] = pd.to_datetime(df_all['open_time'], unit='ms')

# 숫자 컬럼 변환
for col in ['open', 'high', 'low', 'close', 'volume']:
    df_all[col] = pd.to_numeric(df_all[col])

print(f"   총 데이터 개수: {len(df_all):,}개 (1분봉)")
print(f"   기간: {df_all['timestamp'].min()} ~ {df_all['timestamp'].max()}")
print(f"   일수: {(df_all['timestamp'].max() - df_all['timestamp'].min()).days}일")
print()

# 3단계: 기본 통계
print("=" * 80)
print("📈 3️⃣ 가격 기본 통계")
print("=" * 80)
print()

print(f"   최저가: ${df_all['low'].min():,.2f}")
print(f"   최고가: ${df_all['high'].max():,.2f}")
print(f"   평균가: ${df_all['close'].mean():,.2f}")
print(f"   중앙값: ${df_all['close'].median():,.2f}")
print()

# 4단계: 1분 변동률 분석
print("=" * 80)
print("📊 4️⃣ 1분 단위 가격 변동률 분석")
print("=" * 80)
print()

# 1분 변동률 계산 (종가 기준)
df_all['price_change_1m'] = df_all['close'].pct_change() * 100

print(f"   평균 변동률: {df_all['price_change_1m'].mean():.4f}%")
print(f"   변동률 표준편차: {df_all['price_change_1m'].std():.4f}%")
print(f"   최대 상승: +{df_all['price_change_1m'].max():.2f}%")
print(f"   최대 하락: {df_all['price_change_1m'].min():.2f}%")
print()

# 변동률 분포
print("   1분 변동률 분포:")
percentiles = [99, 95, 90, 75, 50, 25, 10, 5, 1]
for p in percentiles:
    val = df_all['price_change_1m'].quantile(p/100)
    print(f"   상위 {100-p:2d}% ~ {p:2d}%: {val:+.4f}%")
print()

# 5단계: 일별 변동성 분석
print("=" * 80)
print("📈 5️⃣ 일별 변동성 분석")
print("=" * 80)
print()

df_all['date'] = df_all['timestamp'].dt.date

# 일별 통계
daily_stats = df_all.groupby('date').agg({
    'open': 'first',
    'close': 'last',
    'high': 'max',
    'low': 'min',
    'volume': 'sum'
}).reset_index()

# 일일 변동률
daily_stats['daily_range'] = ((daily_stats['high'] - daily_stats['low']) / daily_stats['low'] * 100)
daily_stats['daily_change'] = ((daily_stats['close'] - daily_stats['open']) / daily_stats['open'] * 100)

print(f"   평균 일일 변동폭: {daily_stats['daily_range'].mean():.2f}%")
print(f"   최대 일일 변동폭: {daily_stats['daily_range'].max():.2f}%")
print(f"   최소 일일 변동폭: {daily_stats['daily_range'].min():.2f}%")
print()
print(f"   평균 일일 등락률: {daily_stats['daily_change'].mean():.2f}%")
print(f"   표준편차: {daily_stats['daily_change'].std():.2f}%")
print()

# 6단계: 레버리지 20배 기준 분석
print("=" * 80)
print("🔥 6️⃣ 레버리지 20배 기준 분석")
print("=" * 80)
print()

df_all['roi_20x'] = df_all['price_change_1m'] * 20

print("   1분봉 기준 ROI (레버리지 20배):")
print(f"   평균 ROI: {df_all['roi_20x'].mean():.2f}%")
print(f"   ROI 표준편차: {df_all['roi_20x'].std():.2f}%")
print(f"   최대 ROI: +{df_all['roi_20x'].max():.2f}%")
print(f"   최소 ROI: {df_all['roi_20x'].min():.2f}%")
print()

# ROI 분포
print("   ROI 20배 분포:")
roi_ranges = [
    (-100, -50, "청산 위험(-100% ~ -50%)"),
    (-50, -20, "큰 손실(-50% ~ -20%)"),
    (-20, -5, "중간 손실(-20% ~ -5%)"),
    (-5, 0, "소폭 손실(-5% ~ 0%)"),
    (0, 5, "소폭 수익(0% ~ +5%)"),
    (5, 20, "중간 수익(+5% ~ +20%)"),
    (20, 50, "큰 수익(+20% ~ +50%)"),
    (50, 100, "매우 큰 수익(+50% ~ +100%)"),
    (100, 1000, "극단적 수익(+100% 이상)")
]

for min_roi, max_roi, label in roi_ranges:
    count = len(df_all[(df_all['roi_20x'] >= min_roi) & (df_all['roi_20x'] < max_roi)])
    pct = count / len(df_all) * 100
    print(f"   {label:30s}: {count:6,}회 ({pct:5.2f}%)")
print()

# 7단계: 연속 상승/하락 분석
print("=" * 80)
print("📉 7️⃣ 연속 상승/하락 분석")
print("=" * 80)
print()

# 상승/하락 방향
df_all['direction'] = np.where(df_all['price_change_1m'] > 0, 1, -1)

# 연속성 계산
df_all['streak'] = (df_all['direction'] != df_all['direction'].shift()).cumsum()
streak_counts = df_all.groupby('streak').size()

print(f"   평균 연속 봉 개수: {streak_counts.mean():.1f}개")
print(f"   최대 연속 봉 개수: {streak_counts.max()}개")
print()

# 8단계: 거래량 분석
print("=" * 80)
print("📦 8️⃣ 거래량 분석")
print("=" * 80)
print()

print(f"   평균 1분 거래량: {df_all['volume'].mean():,.2f} BTC")
print(f"   최대 1분 거래량: {df_all['volume'].max():,.2f} BTC")
print(f"   일평균 거래량: {daily_stats['volume'].mean():,.2f} BTC")
print()

# 9단계: 시간대별 변동성
print("=" * 80)
print("🕐 9️⃣ 시간대별 변동성 분석")
print("=" * 80)
print()

df_all['hour'] = df_all['timestamp'].dt.hour

hourly_volatility = df_all.groupby('hour')['price_change_1m'].agg(['mean', 'std', 'count'])
hourly_volatility['abs_mean'] = df_all.groupby('hour')['price_change_1m'].apply(lambda x: x.abs().mean())

print("   시간대별 평균 변동률 (절댓값):")
print()
print("   시간   평균변동   표준편차    데이터수")
print("   " + "-" * 45)
for hour in range(24):
    if hour in hourly_volatility.index:
        row = hourly_volatility.loc[hour]
        print(f"   {hour:2d}시   {row['abs_mean']:7.4f}%   {row['std']:7.4f}%   {row['count']:8,.0f}개")
print()

# 가장 변동성 큰 시간대
most_volatile_hour = hourly_volatility['abs_mean'].idxmax()
print(f"   🔥 가장 변동성 큰 시간대: {most_volatile_hour}시 (UTC 기준)")
print(f"      → 한국시간: {(most_volatile_hour + 9) % 24}시")
print()

# 10단계: 요약 및 권장사항
print("=" * 80)
print("💡 10️⃣ 분석 요약 및 전략 권장사항")
print("=" * 80)
print()

avg_1m_change = df_all['price_change_1m'].abs().mean()
std_1m_change = df_all['price_change_1m'].std()
avg_daily_range = daily_stats['daily_range'].mean()

print("📊 핵심 지표:")
print(f"   • 1분 평균 변동률: {avg_1m_change:.4f}%")
print(f"   • 1분 변동 표준편차: {std_1m_change:.4f}%")
print(f"   • 일평균 변동폭: {avg_daily_range:.2f}%")
print()

print("🎯 레버리지 20배 기준 권장사항:")
print()

# ROI 권장
suggested_stop_loss_pct = round(std_1m_change * 20 * 3, 0)  # 3 표준편차
suggested_take_profit_pct = round(std_1m_change * 20 * 4, 0)  # 4 표준편차

print(f"   📉 권장 손절 (Stop Loss): ROI -{suggested_stop_loss_pct:.0f}%")
print(f"      → 가격 변동: 약 {suggested_stop_loss_pct/20:.1f}%")
print()
print(f"   📈 권장 익절 (Take Profit): ROI +{suggested_take_profit_pct:.0f}%")
print(f"      → 가격 변동: 약 {suggested_take_profit_pct/20:.1f}%")
print()

# 예상 거래 빈도
daily_candles = 1440  # 하루 1440분
estimated_signals_per_day = daily_candles * 0.01  # 임시 추정치

print("   💼 예상 거래 특성:")
print(f"      • 일일 데이터 포인트: {daily_candles}개 (1분봉)")
print(f"      • 변동성이 큰 시간대: {most_volatile_hour}시 (UTC) = 한국 {(most_volatile_hour + 9) % 24}시")
print()

print("=" * 80)
print("✅ 분석 완료!")
print("=" * 80)
print()
print("다음 단계:")
print("   1. 이 데이터를 바탕으로 전략 파라미터 조정")
print("   2. RSI, EMA 등 기술적 지표 계산")
print("   3. 백테스팅 시뮬레이션 실행")
print()
