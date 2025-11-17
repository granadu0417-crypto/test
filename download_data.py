"""
바이낸스 선물 거래 데이터 다운로드 프로그램
- BTCUSDT 1년치 1분봉 데이터를 다운로드합니다
"""

import datetime
from binance_historical_data import BinanceDataDumper

print("=" * 60)
print("바이낸스 선물 데이터 다운로드 프로그램")
print("=" * 60)
print()

# 1단계: 다운로드 설정
print("📋 1단계: 다운로드 설정 중...")
print()

# 데이터를 저장할 폴더와 설정을 지정합니다
data_dumper = BinanceDataDumper(
    path_dir_where_to_dump="./data",      # 데이터를 저장할 폴더
    asset_class="um",                      # um = USD 마진 선물 (BTCUSDT 같은 거래)
    data_type="klines",                    # klines = 캔들스틱 데이터 (봉 데이터)
    data_frequency="1m",                   # 1m = 1분봉
)

print("✅ 설정 완료!")
print(f"   - 저장 위치: ./data 폴더")
print(f"   - 거래소: 바이낸스 선물 (USD 마진)")
print(f"   - 데이터 타입: 1분봉 캔들스틱")
print()

# 2단계: 다운로드할 기간 설정
print("📅 2단계: 다운로드 기간 설정...")
print()

# 1년 전부터 오늘까지의 데이터
date_end = datetime.date.today()                         # 오늘 날짜
date_start = date_end - datetime.timedelta(days=365)     # 1년 전

print(f"   시작 날짜: {date_start}")
print(f"   종료 날짜: {date_end}")
print(f"   총 기간: 약 1년")
print()

# 3단계: 데이터 다운로드 시작
print("⏬ 3단계: 데이터 다운로드 시작...")
print("   (이 작업은 몇 분 정도 걸릴 수 있습니다)")
print()

try:
    data_dumper.dump_data(
        tickers=["BTCUSDT"],           # 비트코인 USDT 선물
        date_start=date_start,
        date_end=date_end,
        is_to_update_existing=False    # 기존 데이터를 덮어쓰지 않음
    )

    print()
    print("=" * 60)
    print("✅ 다운로드 완료!")
    print("=" * 60)
    print()
    print("📁 다운로드된 데이터 위치: ./data 폴더")
    print("📊 다음 단계: 데이터를 확인하고 시각화할 수 있습니다")
    print()

except Exception as e:
    print()
    print("❌ 오류가 발생했습니다:")
    print(f"   {str(e)}")
    print()
    print("💡 해결 방법:")
    print("   1. 인터넷 연결을 확인하세요")
    print("   2. 잠시 후 다시 시도해보세요")
    print()
