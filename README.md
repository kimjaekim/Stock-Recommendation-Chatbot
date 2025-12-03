# Stock Recommendation Chatbot

AI 기반 주식 추천·검증 대시보드를 제공하는 Spring Boot 웹앱입니다. `/` 진입 시 정적 `index.html`로 포워딩해 PWA 메타 정보와 서비스 워커를 로드하고, 멀티 타임프레임 예측·포트폴리오·검증 기능을 한 화면에서 제공합니다.

## 주요 기능
- **랜딩 페이지 & PWA**: 타임프레임(1/3/5/10일) 선택, 포트폴리오/오늘의 검증 모달 버튼, 듀얼 게이지(위험도·변동성), 채팅 인터페이스를 포함한 대시보드를 정적 리소스로 제공하며, 서비스 워커 등록과 설치 프롬프트/푸시 권한 요청으로 PWA를 구성합니다.【F:src/main/java/com/future/my/controller/HomeController.java†L8-L18】【F:src/main/resources/static/index.html†L1-L123】【F:src/main/resources/static/index.html†L154-L193】
- **시장 안전도 대시보드**: `/api/chat/market-status`에서 예측 데이터를 집계해 총 종목 수, 안전·저변동 비율, 시장 코멘트를 계산하고 Chart.js 도넛 게이지로 시각화합니다.【F:src/main/java/com/future/my/controller/ChatbotController.java†L24-L114】【F:src/main/resources/static/js/chat.js†L19-L92】【F:src/main/resources/static/js/chat.js†L95-L164】
- **챗봇 메시지 및 멀티 타임프레임 분석**: `/api/chat/message`가 단일 챗 응답을 반환하고, `/api/chat/multi-timeframe`는 12개 모델 기반 멀티 타임프레임 응답(차트/추천/비교 데이터 포함)을 제공합니다.【F:src/main/java/com/future/my/controller/ChatbotController.java†L26-L58】【F:src/main/java/com/future/my/controller/ChatbotController.java†L116-L173】
- **종목 정보 조회**: 안전 종목 목록, 특정 종목 세부 정보, 간이 차트 이미지를 반환하는 `/api/chat/safe-stocks`, `/api/chat/stock/{ticker}`, `/api/chat/stock/{ticker}/chart` API를 제공합니다.【F:src/main/java/com/future/my/controller/ChatbotController.java†L118-L145】
- **포트폴리오 관리**: `/api/portfolio`에서 포트폴리오와 예측을 함께 조회하고, `/api/portfolio/add`, `/api/portfolio/remove/{ticker}`, `/api/portfolio/clear`로 추가·삭제·초기화 작업을 처리합니다.【F:src/main/java/com/future/my/controller/PortfolioController.java†L14-L83】
- **오늘의 예측 검증**: `/api/verification/today`가 외부 Python 스크립트를 실행해 정확도, 추천 종목 수, 평균 수익률을 JSON으로 반환합니다.【F:src/main/java/com/future/my/controller/VerificationController.java†L18-L74】
- **백테스팅 결과 조회**: `/api/backtest`가 백테스트 결과를 생성해 응답합니다.【F:src/main/java/com/future/my/controller/BacktestController.java†L11-L34】

## 클라이언트 동작
- DOM 로드 시 시장 안전도 API를 호출하고, 응답 구조가 없을 때를 대비한 방어 로직을 포함합니다.【F:src/main/resources/static/js/chat.js†L19-L63】
- 듀얼 게이지를 생성할 때 고해상도 렌더링, 그래디언트, 안전/위험 및 저/고변동 색상 표시를 적용하며, 전체 종목이 0일 때는 차트를 건너뜁니다.【F:src/main/resources/static/js/chat.js†L95-L164】
- 메시지 전송 버튼과 엔터 키 입력을 처리해 챗봇 API로 요청을 보냅니다.【F:src/main/resources/static/js/chat.js†L21-L31】

## 서버 구성
- `JusicApplication`에서 Spring Boot 애플리케이션을 기동합니다.【F:src/main/java/com/future/my/JusicApplication.java†L1-L12】
- 주요 API는 `com.future.my.controller` 패키지에 위치하며, 서비스 계층(`service`)과 도메인 객체(`domain`)를 통해 예측·차트·포트폴리오 로직을 분리합니다.

## 실행
이 저장소에는 빌드 스크립트가 포함되어 있지 않으며, 기존 환경에서 실행 가능한 상태로 제공됩니다. Spring Boot 프로젝트로 import한 뒤 애플리케이션을 실행하면 루트 경로(`/`)에서 대시보드 UI에 접근할 수 있습니다.
