# 🎯 '안전한 낚시터' 챗봇 시스템 운영 가이드

## 📋 시스템 개요

**'안전한 낚시터'**는 AI 기반 주식 투자 추천 챗봇 시스템입니다. 사용자의 투자 금액과 안전성 요구사항에 따라 최적의 주식 포트폴리오를 추천합니다.

## 🏗️ 시스템 아키텍처

```
📁 안전한낚시터/
├── 🤖 멀티 타임프레임 챗봇 (매일 응답)
│   ├── today_predictions_1day.json (매일 업데이트)
│   ├── today_predictions_3day.json
│   ├── today_predictions_5day.json
│   ├── today_predictions_10day.json
│   └── multi_timeframe_chatbot.py (메인 챗봇)
├── ⚙️ 백엔드 (데이터 관리)
│   ├── predict_daily_multitf.py (매일 실행)
│   ├── final_multi_timeframe_models.pkl (12개 모델 저장)
│   └── chatbot_cli.py (Spring Boot 연동)
└── 🌐 웹 서비스
    ├── Spring Boot API
    └── React Frontend
```

## ⚙️ 시스템 운영 방식

### 1. 💬 챗봇의 역할 (사용자 응답)

**사용자 요청 예시**: 
- "100만원으로 안전하게 추천해줘" (기본: 5일 예측)
- "내일 삼성전자 어때?" (1일 예측)
- "다음주 추천 종목은?" (10일 예측)
- "이번주 SK하이닉스 vs 삼성전자" (5일 예측, 종목 비교)

**멀티 타임프레임 챗봇 로직** (`multi_timeframe_chatbot.py`):
1. **타임프레임 자동 감지**: 메시지에서 1일/3일/5일/10일 키워드 추출
2. **종목 추출**: 티커 또는 한글 종목명 인식
3. **모델 선택**: 해당 타임프레임의 12개 모델 중 Direction/Volatility/Risk 모델 자동 선택
4. **예측 수행**: 최신 차트 데이터로 방향성/변동성/위험도 예측
5. **종합 점수 계산**: 3가지 예측을 가중합하여 투자 점수 산출
6. **추천 등급**: 강력 매수/매수/보유/매도/강력 매도 분류
7. **최종 답변**: 구체적인 분석 결과 및 추천 제시

### 2. ⚙️ 시스템의 역할 (데이터 업데이트)

#### A) 매일 하는 일: 멀티 타임프레임 예측 생성

**목적**: 저장된 12개 모델을 사용해 모든 타임프레임(1/3/5/10일)의 예측 생성

**실행 시간**: 매일 장 마감 후 (오후 6시)

**실행 방법**:
```bash
# 모든 타임프레임 예측 생성
py predict_daily_multitf.py 1day
py predict_daily_multitf.py 3day
py predict_daily_multitf.py 5day
py predict_daily_multitf.py 10day

# 또는 스크립트로 한번에 실행
```

**수행 작업**:
1. 오늘 자 데이터를 포함한 최신 차트 데이터 다운로드
2. `final_multi_timeframe_models.pkl`에서 12개 모델 로드
3. 각 타임프레임별로 Direction/Volatility/Risk 예측 수행
4. 결과를 `today_predictions_1day.json`, `today_predictions_3day.json`, `today_predictions_5day.json`, `today_predictions_10day.json` 파일에 저장
5. 검증용 날짜별 파일도 함께 생성: `predictions_1day_YYYY-MM-DD.json` 등

#### B) 모델 재학습 (필요시 수동 실행)

**목적**: 최신 데이터로 12개 멀티 타임프레임 모델 재훈련

**실행 시간**: 필요시 수동 실행 (예: 월 1회 또는 시장 변동 큰 시기)

**실행 방법**:
```bash
# 멀티 타임프레임 모델 재학습 (현재는 수동 실행)
# 향후 자동화 스크립트 추가 예정
```

**수행 작업**:
1. 1/3/5/10일 × Direction/Volatility/Risk = 12개 모델 각각 데이터 수집
2. 각 모델별 최적 기간 및 특성으로 데이터셋 구축
3. 12개 모델을 각각 재훈련
4. `final_multi_timeframe_models.pkl` 파일 업데이트
5. 성능 검증 및 리포트 생성

## 🚀 시스템 시작하기

### 1. 초기 설정

```bash
# 멀티 타임프레임 모델이 이미 final_multi_timeframe_models.pkl에 저장되어 있음

# 1. 일일 예측 실행 (모든 타임프레임)
py predict_daily_multitf.py 1day
py predict_daily_multitf.py 3day
py predict_daily_multitf.py 5day
py predict_daily_multitf.py 10day

# 2. 챗봇 테스트
python -c "from multi_timeframe_chatbot import MultiTimeframeChatbot; bot = MultiTimeframeChatbot(); print(bot.chat('내일 삼성전자 어때?'))"
```

### 2. 정기 운영

#### 매일 (장 마감 후)
```bash
# 모든 타임프레임 예측 생성
py predict_daily_multitf.py 1day
py predict_daily_multitf.py 3day
py predict_daily_multitf.py 5day
py predict_daily_multitf.py 10day
```

#### 모델 재학습 (필요시)
```bash
# 향후 자동화 스크립트 추가 예정
# 현재는 수동 실행 또는 final_hybrid_optimal_system.py 참고
```

## 📊 모델 성능

### 멀티 타임프레임 모델 시스템 (12개 모델)

#### 모델 구성
- **Direction 모델**: StackingClassifier (4개: 1/3/5/10일)
- **Volatility 모델**: LogisticRegression (4개: 1/3/5/10일)
- **Risk 모델**: LogisticRegression (4개: 1/3/5/10일)

#### Test Accuracy (최신 평가 기준)
**Direction 모델:**
- 1일: 51.7%
- 3일: 48.6%
- 5일: 49.7%
- 10일: 49.9%

**Volatility 모델:**
- 1일: 47.3%
- 3일: 62.9%
- 5일: 66.1%
- 10일: 70.5%

**Risk 모델:**
- 1일: 59.3%
- 3일: 57.9%
- 5일: 56.4%
- 10일: 53.7%

### 성능 특징
- **Volatility 모델**: 기간이 길수록 성능 향상 (10일 70.5%)
- **Direction 모델**: 단기 예측 어려움 (시장 노이즈 영향)
- **Risk 모델**: 단기 위험 감지 효과적 (1일 59.3%)
- **기준선**: 50% (2지선다)

## 🔧 문제 해결

### 1. 안전한 종목이 없는 경우
- **원인**: 모델이 보수적으로 설정됨
- **해결**: Risk/Volatility 임계값 조정 또는 모델 재훈련

### 2. 예측 정확도가 낮은 경우
- **원인**: 시장 상황 변화 또는 모델 노화
- **해결**: 주간 모델 재학습 실행

### 3. 데이터 수집 실패
- **원인**: 네트워크 문제 또는 yfinance API 제한
- **해결**: 재시도 또는 수동 데이터 업데이트

## 📈 성능 모니터링

### 1. 일일 모니터링
- `today_predictions_1day.json`, `today_predictions_3day.json`, `today_predictions_5day.json`, `today_predictions_10day.json` 파일 확인
- 각 타임프레임별 안전한 종목 수량 체크
- 예측 확률 분포 확인
- 모델 정확도 정보 확인 (각 예측에 포함됨)

### 2. 주간 모니터링
- 모델 성능 지표 확인
- 과적합 여부 검사
- 데이터 품질 평가

## 🎯 향후 개선사항

### 1. 단기 개선
- [ ] 웹 인터페이스 구축
- [ ] 실시간 알림 시스템
- [ ] 포트폴리오 성과 추적

### 2. 중기 개선
- [ ] 더 많은 기술적 지표 추가
- [ ] 시장 상황별 모델 전환
- [ ] 사용자 맞춤형 추천

### 3. 장기 개선
- [ ] 딥러닝 모델 도입
- [ ] 뉴스 감성 분석 통합
- [ ] 글로벌 시장 확장

## 📞 지원 및 문의

시스템 운영 중 문제가 발생하면 다음을 확인하세요:

1. **로그 파일**: 실행 로그 확인
2. **데이터 파일**: `today_predictions_*.json`, `final_multi_timeframe_models.pkl` 파일 상태 확인
3. **네트워크**: 인터넷 연결 및 yfinance API 접근 가능성 확인
4. **모델 파일**: `final_multi_timeframe_models.pkl` 정상 로드 여부 확인

---

**🎉 '안전한 낚시터' 멀티 타임프레임 시스템이 성공적으로 구축되었습니다!**

### 주요 특징
- ✅ 12개 모델로 1/3/5/10일 예측 지원
- ✅ 사용자 요청에 따라 타임프레임 자동 감지
- ✅ 종목 분석, 추천, 비교 기능 제공
- ✅ Spring Boot 연동 가능 (`chatbot_cli.py`)

이제 Spring Boot + React 웹 서비스 개발을 시작할 준비가 완료되었습니다.

