"""
종목명 매핑 테이블
티커 코드와 실제 종목명을 매핑
"""

STOCK_NAME_MAPPING = {
    '005930.KS': '삼성전자',
    '000660.KS': 'SK하이닉스',
    '051910.KS': 'LG화학',
    '035420.KS': 'NAVER',
    '035720.KS': '카카오',
    '005380.KS': '현대차',
    '000270.KS': '기아',
    '068270.KS': '셀트리온',
    '207940.KS': '삼성바이오로직스',
    '005490.KS': 'POSCO',
    '006400.KS': '삼성SDI',
    '051900.KS': 'LG생활건강',
    '028260.KS': '삼성물산',
    '012330.KS': '현대모비스',
    '066570.KS': 'LG전자',
    '003550.KS': 'LG',
    '096770.KS': 'SK이노베이션',
    '017670.KS': 'SK텔레콤',
    '009150.KS': '삼성전기',
    '034730.KS': 'SK',
    '000720.KS': '현대건설',
    '003490.KS': '대한항공',
    '011200.KS': 'HMM',
    '012450.KS': '한화에어로스페이스',
    '015760.KS': '한국전력',
    '016360.KS': '삼성생명',
    '017800.KS': '현대엘리베이',
    '018880.KS': '한온시스템',
    '020150.KS': '일동제약',
    '021240.KS': '코웨이'
}

def get_stock_name(ticker):
    """티커 코드로 종목명 조회"""
    return STOCK_NAME_MAPPING.get(ticker, ticker)

def get_all_stock_names():
    """모든 종목명 반환"""
    return STOCK_NAME_MAPPING

if __name__ == "__main__":
    # 테스트
    print("종목명 매핑 테이블:")
    for ticker, name in STOCK_NAME_MAPPING.items():
        print(f"{ticker}: {name}")

