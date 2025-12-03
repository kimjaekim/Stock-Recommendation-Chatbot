"""
주식 감정분석용 한국어 키워드 사전
"""

# 긍정 키워드 (주가 상승 예상)
POSITIVE_KEYWORDS = [
    # 실적 관련
    '실적 개선', '영업이익 증가', '매출 증가', '흑자 전환', '어닝 서프라이즈',
    '목표가 상향', '투자의견 상향', '신고가', '사상 최대', '역대 최대',
    
    # 성장 관련
    '성장', '확대', '증가', '상승', '호조', '개선', '회복', '반등',
    '급등', '강세', '돌파', '상승세', '성장세', '호실적', '호재',
    
    # 투자/사업 관련
    '대규모 투자', '신규 계약', '수주', '인수합병', '제휴', '협력',
    '신사업', '신제품', '혁신', '기술 개발', '특허', '독점',
    
    # 수요 관련
    '수요 증가', '주문 급증', '매출 호조', '판매 증가', '시장 확대',
    '점유율 상승', '경쟁력 강화', '우위', '선도',
    
    # 투자자 관련
    '기관 매수', '외국인 순매수', '대량 매수', '추천', '매수 의견',
    '적극 매수', '비중 확대', '목표주가 상향',
    
    # 기타
    '호황', '긍정적', '유망', '기대', '전망 밝음', '낙관', '청신호'
]

# 부정 키워드 (주가 하락 예상)
NEGATIVE_KEYWORDS = [
    # 실적 관련
    '실적 악화', '영업이익 감소', '매출 감소', '적자', '어닝 쇼크',
    '목표가 하향', '투자의견 하향', '부진', '저조', '감소',
    
    # 하락 관련
    '하락', '급락', '폭락', '약세', '부진', '악화', '침체', '위축',
    '하락세', '약세장', '조정', '하방', '저조',
    
    # 위험 관련
    '리스크', '우려', '불확실성', '위험', '경고', '우려', '문제',
    '위기', '악재', '충격', '타격', '손실', '적자',
    
    # 규제/법적
    '규제', '제재', '소송', '분쟁', '조사', '압수수색', '기소',
    '과징금', '벌금', '제한', '금지',
    
    # 경영 문제
    '경영 악화', '구조조정', '감원', '폐쇄', '철수', '포기',
    '중단', '연기', '취소', '실패',
    
    # 투자자 관련
    '기관 매도', '외국인 순매도', '대량 매도', '매도 의견',
    '비중 축소', '투자 중단',
    
    # 기타
    '불황', '부정적', '비관', '우려', '전망 어두움', '적신호', '경고'
]

# 중립 키워드 (필터링용)
NEUTRAL_KEYWORDS = [
    '발표', '공시', '보고', '예정', '계획', '검토', '논의',
    '회의', '참석', '방문', '일정', '진행'
]

def get_positive_keywords():
    """긍정 키워드 반환"""
    return POSITIVE_KEYWORDS

def get_negative_keywords():
    """부정 키워드 반환"""
    return NEGATIVE_KEYWORDS

def get_neutral_keywords():
    """중립 키워드 반환"""
    return NEUTRAL_KEYWORDS

def calculate_sentiment_score(text):
    """
    텍스트의 감정 점수 계산
    
    Args:
        text: 뉴스 제목 또는 본문
    
    Returns:
        float: -1 (매우 부정) ~ +1 (매우 긍정)
    """
    if not text:
        return 0.0
    
    positive_count = sum(1 for keyword in POSITIVE_KEYWORDS if keyword in text)
    negative_count = sum(1 for keyword in NEGATIVE_KEYWORDS if keyword in text)
    
    total = positive_count + negative_count
    
    if total == 0:
        return 0.0
    
    # 감정 점수: -1 ~ +1
    score = (positive_count - negative_count) / total
    
    return score

def classify_sentiment(score):
    """
    감정 점수를 클래스로 변환
    
    Args:
        score: 감정 점수 (-1 ~ +1)
    
    Returns:
        str: 'positive', 'negative', 'neutral'
    """
    if score > 0.2:
        return 'positive'
    elif score < -0.2:
        return 'negative'
    else:
        return 'neutral'

# 테스트
if __name__ == '__main__':
    print("="*80)
    print("Sentiment Keywords Test")
    print("="*80)
    
    print(f"\nPositive keywords: {len(POSITIVE_KEYWORDS)}")
    print(f"Negative keywords: {len(NEGATIVE_KEYWORDS)}")
    print(f"Neutral keywords: {len(NEUTRAL_KEYWORDS)}")
    
    # 테스트 문장
    test_cases = [
        "삼성전자, 실적 개선으로 목표가 상향 전망",
        "SK하이닉스, 영업이익 감소 우려 확대",
        "NAVER, 신사업 진출 발표",
        "현대차, 대규모 투자로 성장세 기대",
        "카카오, 규제 리스크에 주가 급락"
    ]
    
    print("\n[Test Cases]")
    for text in test_cases:
        score = calculate_sentiment_score(text)
        sentiment = classify_sentiment(score)
        print(f"\nText: {text}")
        print(f"  Score: {score:+.2f}")
        print(f"  Sentiment: {sentiment}")

