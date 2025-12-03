package com.future.my.service;

import com.future.my.domain.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.text.NumberFormat;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * 챗봇 서비스 - 사용자 메시지 분석 및 추천 로직
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class ChatbotService {
    
    private final PredictionService predictionService;
    private final NumberFormat currencyFormat = NumberFormat.getInstance(Locale.KOREA);
    
    /**
     * 사용자 메시지 처리
     * @param request 챗봇 요청
     * @return 챗봇 응답
     */
    public ChatResponse processMessage(ChatRequest request) {
        String message = request.getMessage().trim();
        log.info("💬 사용자 메시지: {}", message);
        
        // 1. 인사말 / 시작
        if (isGreeting(message)) {
            return handleGreeting();
        }
        
        // 2. 시장 상태 조회
        if (isMarketStatusQuery(message)) {
            return handleMarketStatus();
        }
        
        // 3. 특정 종목 분석 요청 (투자 추천보다 우선)
        String ticker = extractTicker(message);
        if (ticker != null) {
            // 종목명이 있으면 분석 요청으로 간주
            return handleStockAnalysis(ticker, message);
        }
        
        // 4. 투자 추천 요청 (금액 포함 또는 의도만)
        Long investmentAmount = extractInvestmentAmount(message);
        if (investmentAmount != null && investmentAmount > 0) {
            return handleInvestmentRecommendation(investmentAmount, message);
        }
        
        // 5. 투자 의도는 있지만 금액이 없는 경우 (기본 100만원)
        if (isInvestmentIntent(message)) {
            log.info("투자 의도 감지 (금액 없음) - 기본 100만원 적용");
            return handleInvestmentRecommendation(1_000_000L, message);
        }
        
        // 6. 도움말 / 기본 응답
        return handleDefault();
    }
    
    /**
     * 인사말 체크 (개선)
     */
    private boolean isGreeting(String message) {
        String normalized = message.toLowerCase().replaceAll("\\s+", "");
        String[] greetings = {
            "안녕", "헬로", "hi", "hello", "시작", "처음", "반가", 
            "하이", "hey", "안뇽", "ㅎㅇ", "ㅎㅎ", "좋은아침", "좋은오후"
        };
        
        for (String greeting : greetings) {
            if (normalized.contains(greeting)) {
                return true;
            }
        }
        
        // 짧은 인사말 정확 매칭
        if (normalized.matches("^(안녕|하이|헬로|hi|hello)$")) {
            return true;
        }
        
        return false;
    }
    
    /**
     * 시장 상태 조회 체크 (개선)
     */
    private boolean isMarketStatusQuery(String message) {
        String normalized = message.toLowerCase().replaceAll("\\s+", "");
        String[] keywords = {
            "시장", "안전도", "상태", "현황", "브리핑", "분위기", 
            "오늘", "지금", "요즘", "어때", "어떻게", "어떤가",
            "전체", "전반", "개관", "개황", "동향", "추세"
        };
        
        for (String keyword : keywords) {
            if (normalized.contains(keyword)) {
                // "시장 어때?", "오늘 어때?", "지금 상황은?" 등 인식
                if (normalized.contains("어때") || normalized.contains("어떻") || 
                    normalized.contains("상황") || normalized.contains("시장")) {
                    return true;
                }
            }
        }
        
        // 짧은 질문 패턴
        if (normalized.matches(".*(시장|상황|오늘|지금|요즘).*(어때|어떻|상태|현황).*")) {
            return true;
        }
        
        return false;
    }
    
    /**
     * 투자 의도 체크 (개선)
     */
    private boolean isInvestmentIntent(String message) {
        String normalized = message.toLowerCase().replaceAll("\\s+", "");
        String[] intentKeywords = {
            "추천", "알려줘", "알려주", "보여줘", "보여주", "찾아줘", "찾아주",
            "골라줘", "골라주", "선택", "고르", "투자", "매수", "사자", "살까",
            "뭐살까", "뭐사", "어디", "어떤", "좋은", "괜찮", "안전한", "종목"
        };
        
        for (String keyword : intentKeywords) {
            if (normalized.contains(keyword)) {
                return true;
            }
        }
        
        return false;
    }
    
    /**
     * 추천 개수 추출 (신규)
     */
    private int extractRecommendationCount(String message) {
        String normalized = message.replaceAll("\\s+", "");
        
        // 패턴 1: "3개 추천", "5개 추천", "10개"
        Pattern pattern1 = Pattern.compile("(\\d+)개");
        Matcher matcher1 = pattern1.matcher(normalized);
        if (matcher1.find()) {
            try {
                int count = Integer.parseInt(matcher1.group(1));
                if (count >= 1 && count <= 10) {
                    log.info("추천 개수 추출: {}개", count);
                    return count;
                }
            } catch (NumberFormatException e) {
                // 무시
            }
        }
        
        // 기본값: 3개
        return 3;
    }
    
    /**
     * 투자 금액 추출 (개선)
     */
    private Long extractInvestmentAmount(String message) {
        // 시간 단위 필터링 (금액이 아닌 시간을 제외)
        if (message.matches(".*\\d+\\s*(일|주|달|개월|년|시간|분|초).*")) {
            return null;
        }
        
        String normalized = message.replaceAll("\\s+", "");
        
        // 패턴 1: 숫자 + 만원, 억원, 천원, 원
        Pattern pattern1 = Pattern.compile("(\\d+(?:,\\d+)*)\\s*([만억천]?원?)");
        Matcher matcher1 = pattern1.matcher(message);
        
        while (matcher1.find()) {
            String numberStr = matcher1.group(1).replace(",", "");
            String unit = matcher1.group(2);
            
            try {
                long number = Long.parseLong(numberStr);
                
                if (unit.contains("억")) {
                    return number * 100_000_000L;
                } else if (unit.contains("만")) {
                    return number * 10_000L;
                } else if (unit.contains("천")) {
                    return number * 1_000L;
                } else if (number > 10000) {
                    // 큰 숫자는 원 단위로 간주
                    return number;
                }
            } catch (NumberFormatException e) {
                log.warn("금액 파싱 실패: {}", numberStr);
            }
        }
        
        // 패턴 2: "백만", "천만", "백" 등
        if (normalized.contains("백만")) {
            return 1_000_000L;
        } else if (normalized.contains("천만")) {
            return 10_000_000L;
        } else if (normalized.matches(".*\\d+백.*")) {
            Matcher m = Pattern.compile("(\\d+)백").matcher(normalized);
            if (m.find()) {
                return Long.parseLong(m.group(1)) * 1_000_000L;
            }
        }
        
        // 투자 의도는 있지만 금액이 없으면 기본값 (100만원)
        if (isInvestmentIntent(message)) {
            return 1_000_000L;
        }
        
        return null;
    }
    
    /**
     * 티커 또는 종목명 추출 (30개 전체 매핑)
     */
    private String extractTicker(String message) {
        String normalized = message.replaceAll("\\s+", "").toLowerCase();
        
        // 30개 종목 전체 매핑 (종목명 → 티커)
        java.util.Map<String, String> stockMap = new java.util.HashMap<>();
        
        // 삼성 계열
        stockMap.put("삼성전자", "005930.KS");
        stockMap.put("삼성sdi", "006400.KS");
        stockMap.put("삼성물산", "028260.KS");
        stockMap.put("삼성전기", "009150.KS");
        stockMap.put("삼성생명", "016360.KS");
        stockMap.put("삼성바이오로직스", "207940.KS");
        stockMap.put("삼성바이오", "207940.KS");
        
        // SK 계열
        stockMap.put("sk하이닉스", "000660.KS");
        stockMap.put("하이닉스", "000660.KS");
        stockMap.put("sk이노베이션", "096770.KS");
        stockMap.put("sk텔레콤", "017670.KS");
        stockMap.put("sk", "034730.KS");
        
        // LG 계열
        stockMap.put("lg화학", "051910.KS");
        stockMap.put("lg생활건강", "051900.KS");
        stockMap.put("lg전자", "066570.KS");
        stockMap.put("lg", "003550.KS");
        
        // 현대 계열
        stockMap.put("현대차", "005380.KS");
        stockMap.put("현대모비스", "012330.KS");
        stockMap.put("현대건설", "000720.KS");
        stockMap.put("현대엘리베이", "017800.KS");
        
        // IT/통신
        stockMap.put("네이버", "035420.KS");
        stockMap.put("naver", "035420.KS");
        stockMap.put("카카오", "035720.KS");
        stockMap.put("셀트리온", "068270.KS");
        
        // 기타
        stockMap.put("기아", "000270.KS");
        stockMap.put("포스코", "005490.KS");
        stockMap.put("posco", "005490.KS");
        stockMap.put("대한항공", "003490.KS");
        stockMap.put("hmm", "011200.KS");
        stockMap.put("한화에어로스페이스", "012450.KS");
        stockMap.put("한화에어로", "012450.KS");
        stockMap.put("한국전력", "015760.KS");
        stockMap.put("한전", "015760.KS");
        stockMap.put("한온시스템", "018880.KS");
        stockMap.put("일동제약", "020150.KS");
        stockMap.put("코웨이", "021240.KS");
        
        // 매핑 테이블에서 검색
        for (java.util.Map.Entry<String, String> entry : stockMap.entrySet()) {
            String stockName = entry.getKey().toLowerCase();
            String ticker = entry.getValue();
            
            if (normalized.contains(stockName)) {
                log.info("종목 매칭: {} → {}", stockName, ticker);
                return ticker;
            }
        }
        
        // "삼성" 단독 → 삼성전자
        if (normalized.matches(".*삼성[^전sdb물모생바].*") || 
            normalized.equals("삼성")) {
            return "005930.KS";
        }
        
        // "lg" 단독 → LG
        if (normalized.equals("lg") || normalized.equals("엘지")) {
            return "003550.KS";
        }
        
        // "현대" 단독 → 현대차
        if (normalized.matches(".*현대[^모건엘].*") || 
            normalized.equals("현대")) {
            return "005380.KS";
        }
        
        return null;
    }
    
    /**
     * 인사말 응답
     */
    private ChatResponse handleGreeting() {
        double safetyRate = predictionService.getMarketSafetyRate();
        String date = predictionService.getPredictionDate();
        
        String message = String.format(
                "🌊 안녕하세요! '안전한 낚시터' 챗봇입니다.\n\n" +
                "📅 오늘 날짜: %s\n" +
                "📊 현재 시장 안전도: %.1f%%\n\n" +
                "💡 도움말:\n" +
                "• \"100만원 안전하게 추천해줘\" - 투자 추천\n" +
                "• \"시장 상태\" - 시장 안전도 확인\n" +
                "• \"삼성전자 분석해줘\" - 특정 종목 분석\n\n" +
                "궁금하신 것을 말씀해주세요!",
                date, safetyRate * 100
        );
        
        return ChatResponse.builder()
                .message(message)
                .type("greeting")
                .marketSafetyRate(safetyRate)
                .build();
    }
    
    /**
     * 시장 상태 응답
     */
    private ChatResponse handleMarketStatus() {
        // 확률 기반 안전도 계산 (prediction 대신 probability 사용)
        double safetyRate = calculateProbabilityBasedSafetyRate();
        int totalCount = predictionService.getAllPredictions().getTotalStocks();
        String date = predictionService.getPredictionDate();
        
        // 확률 기반 안전 종목 수 계산
        int probabilitySafeCount = (int) Math.round(safetyRate * totalCount);
        
        // 변동성 정보 추가
        double volatilityRate = predictionService.getMarketVolatilityRate();
        int lowVolCount = predictionService.getLowVolatilityStocksCount();
        
        String emoji = safetyRate >= 0.5 ? "😊" : safetyRate >= 0.3 ? "😐" : "😰";
        String level = safetyRate >= 0.5 ? "좋음" : safetyRate >= 0.3 ? "보통" : "주의";
        
        String message = String.format(
                "🌊 오늘의 주식 시장 '안전도' 수준입니다.\n\n" +
                "📅 날짜: %s\n" +
                "📊 시장 안전도: %.1f%% %s\n" +
                "🛡️ 안전 종목: %d개 / 전체 %d개\n" +
                "📉 변동성 안전도: %.1f%%\n" +
                "⚠️ 안전 수준: %s\n\n" +
                "추천을 원하시면 \"100만원 안전하게 추천해줘\"처럼 말씀해주세요.",
                date, safetyRate * 100, emoji, probabilitySafeCount, totalCount, volatilityRate * 100, level
        );
        
        // Chart.js용 시장 안전도 데이터
        java.util.Map<String, Object> chartDataMap = new java.util.HashMap<>();
        java.util.Map<String, Object> marketSafetyChart = new java.util.HashMap<>();
        marketSafetyChart.put("labels", java.util.Arrays.asList("안전", "위험"));
        marketSafetyChart.put("values", java.util.Arrays.asList(probabilitySafeCount, totalCount - probabilitySafeCount));
        marketSafetyChart.put("colors", java.util.Arrays.asList("#4caf50", "#f44336"));
        chartDataMap.put("marketSafety", marketSafetyChart);
        
        // 시장 상태 코멘트 생성
        String marketComment = generateMarketComment(safetyRate, volatilityRate);
        
        // 시장 안전도 상세 정보
        MarketSafetyInfo marketSafety = MarketSafetyInfo.builder()
                .totalStocks(totalCount)
                .safeStocks(probabilitySafeCount) // 확률 기반 개수 사용
                .riskyStocks(totalCount - probabilitySafeCount)
                .safetyRate(safetyRate * 100)
                .lowVolatilityStocks(lowVolCount)
                .highVolatilityStocks(totalCount - lowVolCount)
                .volatilityRate(volatilityRate * 100)
                .marketComment(marketComment)
                .build();
        
        return ChatResponse.builder()
                .message(message)
                .type("market_status")
                .marketSafetyRate(safetyRate)
                .chartData(chartDataMap)
                .marketSafety(marketSafety)
                .build();
    }
    
    /**
     * 타임프레임 감지
     */
    private String detectTimeframe(String message) {
        if (message.contains("내일") || message.contains("1일")) {
            return "1day";
        } else if (message.contains("3일") || message.contains("모레")) {
            return "3day";
        } else if (message.contains("10일") || message.contains("장기") || message.contains("2주")) {
            return "10day";
        }
        // 기본값: 5day (이번주)
        return "5day";
    }
    
    /**
     * 투자 추천 응답
     */
    private ChatResponse handleInvestmentRecommendation(Long amount, String message) {
        boolean isSafetyRequested = message.contains("안전") || message.contains("안정");
        
        // 타임프레임 감지
        String timeframe = detectTimeframe(message);
        PredictionResponse timeframeData = predictionService.getPredictionsByTimeframe(timeframe);
        
        // 추천 개수 추출
        int requestedCount = extractRecommendationCount(message);
        
        log.info("📅 감지된 타임프레임: {}", timeframe);
        log.info("📊 요청 종목 개수: {}개", requestedCount);
        
        List<StockPrediction> candidates;
        String recommendationType = "안전&상승";
        
        if (isSafetyRequested) {
            // 안전&상승 종목 우선 (타임프레임 데이터 사용)
            candidates = getSafeAndUpwardStocksFromData(timeframeData);
            log.info("🔍 1단계: 안전&상승 후보 = {}개", candidates.size());
            
            if (candidates.isEmpty()) {
                // 안전 종목만
                candidates = getSafeStocksFromData(timeframeData);
                recommendationType = "안전";
                log.info("🔍 2단계: 안전 종목 후보 = {}개", candidates.size());
            }
            if (candidates.isEmpty()) {
                // 안전한 종목이 없으면: 3가지 조건을 모두 만족하는 종목 찾기
                candidates = timeframeData.getPredictions().values().stream()
                        .filter(stock -> {
                            // 조건 1: 위험도가 상대적으로 낮을 것 (확률 < 75%)
                            boolean lowRisk = stock.getRisk().getProbability() < 0.75;
                            
                            // 조건 2: 변동성이 낮을 것 (Volatility=0만 허용!)
                            boolean lowVolatility = stock.getVolatility().getPrediction() == 0;
                            
                            // 조건 3: 상승 예측이거나 상승 가능성이 높을 것
                            boolean upwardExpected;
                            if (stock.getDirection().getPrediction() == 1) {
                                upwardExpected = true; // 상승 예측
                            } else {
                                // 하락 예측이지만 확률 < 50%면 실제로는 상승 가능성 높음
                                upwardExpected = stock.getDirection().getProbability() < 0.50;
                            }
                            
                            return lowRisk && lowVolatility && upwardExpected;
                        })
                        .sorted((a, b) -> Double.compare(
                                a.getRisk().getProbability(), 
                                b.getRisk().getProbability()
                        ))
                        .collect(java.util.stream.Collectors.toList());  // limit 제거
                recommendationType = "상대적 안전 (저위험+저변동+상승)";
                log.info("🔍 3단계: 상대적 안전 후보 = {}개", candidates.size());
            }
        } else {
            // 전체 종목에서 상승 기대 (타임프레임 데이터 사용)
            candidates = getSafeAndUpwardStocksFromData(timeframeData);
            log.info("🔍 1단계: 안전&상승 후보 = {}개", candidates.size());
            
            if (candidates.isEmpty()) {
                // 상승 기대 종목 (prediction=1)
                candidates = timeframeData.getPredictions().values().stream()
                        .filter(StockPrediction::isUpward)
                        .sorted((a, b) -> Double.compare(
                                b.getDirection().getProbability(), 
                                a.getDirection().getProbability()
                        ))
                        .collect(java.util.stream.Collectors.toList());
                recommendationType = "상승 기대";
                log.info("🔍 2단계: 상승 예측(1) 후보 = {}개", candidates.size());
            }
            
            if (candidates.isEmpty() || candidates.size() < requestedCount) {
                // 확률 기반 추천 (probability > 0.5)
                candidates = timeframeData.getPredictions().values().stream()
                        .filter(stock -> {
                            // 상승 확률 > 50% (prediction=0이지만 probability가 0.5 미만)
                            boolean highUpwardProb = stock.getDirection().getPrediction() == 0 
                                    && stock.getDirection().getProbability() < 0.5;
                            // 또는 상승 예측
                            boolean upwardPrediction = stock.getDirection().getPrediction() == 1;
                            
                            return highUpwardProb || upwardPrediction;
                        })
                        .sorted((a, b) -> {
                            // 상승 확률이 높은 순으로 정렬 (probability가 0.5에 가까울수록)
                            double probA = a.getDirection().getPrediction() == 1 
                                    ? a.getDirection().getProbability()
                                    : (1.0 - a.getDirection().getProbability());
                            double probB = b.getDirection().getPrediction() == 1 
                                    ? b.getDirection().getProbability()
                                    : (1.0 - b.getDirection().getProbability());
                            return Double.compare(probB, probA);
                        })
                        .collect(java.util.stream.Collectors.toList());
                recommendationType = "확률 기반 추천 (상승 가능성 > 50%)";
                log.info("🔍 3단계: 확률 기반 후보 = {}개", candidates.size());
            }
        }
        
        if (candidates.isEmpty()) {
            return ChatResponse.builder()
                    .message("😢 죄송합니다. 현재 추천 가능한 종목이 없습니다.\n시장 상황이 매우 좋지 않으니 투자를 보류하시는 것이 좋겠습니다.")
                    .type("recommendation")
                    .build();
        }
        
        // 금액을 종목 수로 균등 배분 (사용자 요청 개수 반영)
        int stockCount = Math.min(candidates.size(), requestedCount);
        long amountPerStock = amount / stockCount;
        
        log.info("📈 최종 추천 종목 수: {}개 (후보: {}개, 요청: {}개)", 
                stockCount, candidates.size(), requestedCount);
        
        List<StockRecommendation> recommendations = new ArrayList<>();
        
        // 대시보드 모드: 텍스트 메시지 없이 데이터만 전송
        
        for (int i = 0; i < stockCount; i++) {
            StockPrediction stock = candidates.get(i);
            
            int shares = (int) (amountPerStock / stock.getCurrentPrice());
            double actualAmount = shares * stock.getCurrentPrice();
            
            StockRecommendation recommendation = StockRecommendation.builder()
                    .ticker(stock.getTicker())
                    .stockName(stock.getStockName())
                    .name(stock.getStockName()) // 프론트엔드용 별칭
                    .currentPrice(stock.getCurrentPrice())
                    .investmentAmount((double) amountPerStock)
                    .shares(shares)
                    .actualAmount(actualAmount)
                    .risk(stock.getRisk().getPrediction())
                    .riskProbability(stock.getRisk().getProbability()) // 확률 추가
                    .volatility(stock.getVolatility().getPrediction())
                    .volatilityProbability(stock.getVolatility().getProbability()) // 확률 추가
                    .direction(stock.getDirection().getPrediction())
                    .directionProbability(stock.getDirection().getProbability())
                    .reason(generateReason(stock))
                    .build();
            
            recommendations.add(recommendation);
            
            String statusEmoji;
            String riskInfo = "";
            if (stock.isSafeAndUpward()) {
                statusEmoji = "🛡️안전, 📉저변동성, 📈상승 기대";
            } else if (stock.isSafe()) {
                statusEmoji = "🛡️안전, 📉저변동성";
            } else if (stock.isUpward()) {
                statusEmoji = "📈상승 기대";
            } else {
                statusEmoji = String.format("⚠️ 위험도 %.1f%%", stock.getRisk().getProbability() * 100);
                riskInfo = " (상대적 안전)";
            }
            
            // 상승 확률 계산: prediction=1이면 그대로, prediction=0이면 1-probability
            double upwardProbability;
            if (stock.getDirection().getPrediction() == 1) {
                upwardProbability = stock.getDirection().getProbability() * 100;
            } else {
                upwardProbability = (1 - stock.getDirection().getProbability()) * 100;
            }
            
            // Recommendation 객체에 upwardProbability 설정
            recommendation.setUpwardProbability(upwardProbability);
        }
        
        // Chart.js용 추천 비교 차트 데이터
        java.util.Map<String, Object> chartDataMap = new java.util.HashMap<>();
        java.util.Map<String, Object> recommendationsChart = new java.util.HashMap<>();
        
        java.util.List<String> stockNames = new ArrayList<>();
        java.util.List<Double> upwardProbs = new ArrayList<>();
        java.util.List<String> colors = new ArrayList<>();
        
        for (StockRecommendation rec : recommendations) {
            stockNames.add(rec.getStockName());
            upwardProbs.add(rec.getUpwardProbability());
            // 상승 확률에 따라 색상 결정
            if (rec.getUpwardProbability() >= 60) {
                colors.add("#4caf50"); // 녹색 (높은 상승 확률)
            } else if (rec.getUpwardProbability() >= 50) {
                colors.add("#ff9800"); // 주황색 (중간 상승 확률)
            } else {
                colors.add("#f44336"); // 빨간색 (낮은 상승 확률)
            }
        }
        
        recommendationsChart.put("labels", stockNames);
        recommendationsChart.put("values", upwardProbs);
        recommendationsChart.put("colors", colors);
        chartDataMap.put("recommendations", recommendationsChart);
        
        // 시장 안전도 정보도 함께 전송 (헤더 게이지용)
        int totalCount = predictionService.getAllPredictions().getTotalStocks();
        double safetyRate = calculateProbabilityBasedSafetyRate();
        
        // 확률 기반 안전 종목 수 계산
        int probabilitySafeCount = (int) Math.round(safetyRate * totalCount);
        
        // 변동성 정보 추가
        double volatilityRate = predictionService.getMarketVolatilityRate();
        int lowVolCount = predictionService.getLowVolatilityStocksCount();
        
        // 타임프레임 설명
        String timeframeDesc;
        switch (timeframe) {
            case "1day": timeframeDesc = "내일"; break;
            case "3day": timeframeDesc = "3일 후"; break;
            case "10day": timeframeDesc = "10일 후"; break;
            default: timeframeDesc = "이번 주"; break;
        }
        
        // 위험한 종목 개수 계산
        long riskyStockCount = recommendations.stream()
                .filter(rec -> rec.getRisk() == 1 || rec.getVolatility() == 1)
                .count();
        
        long highRiskCount = recommendations.stream()
                .filter(rec -> rec.getRisk() == 1)
                .count();
        
        // 시장 상태 코멘트 생성 (추천 타입에 따라 경고 추가)
        String marketComment;
        
        // "확률 기반" 추천일 경우 경고 추가
        if (recommendationType.contains("확률 기반")) {
            if (highRiskCount > 0) {
                marketComment = String.format("⚠️ 위험 경고 (%s 기준): 추천 종목 중 %d개가 손실 위험이 높습니다. " +
                    "하락 예측이지만 상승 가능성(50%% 이상)을 고려한 추천입니다. " +
                    "투자 시 각별한 주의가 필요하며, 소액 분산 투자를 권장합니다. 📉⚠️", 
                    timeframeDesc, highRiskCount);
            } else if (riskyStockCount > 0) {
                marketComment = String.format("⚠️ 주의 (%s 기준): 추천 종목 중 %d개가 변동성이 높습니다. " +
                    "확률 기반 추천이므로 투자 시 주의가 필요합니다. 💡", 
                    timeframeDesc, riskyStockCount);
            } else {
                marketComment = String.format("💡 (%s 기준): 확률 기반 추천입니다. " +
                    "하락 예측이지만 상승 확률이 50%% 이상인 종목들입니다. 신중한 투자를 권장합니다.", 
                    timeframeDesc);
            }
        }
        // "상대적 안전" 추천일 경우 강력한 경고 추가
        else if (recommendationType.contains("상대적")) {
            marketComment = String.format("⚠️ 주의 (%s 기준): 시장 전체가 불안정합니다. " +
                "아래 종목들은 '상대적으로' 안전하지만, 위험도가 높으니 " +
                "투자 시 각별한 주의가 필요합니다.", timeframeDesc);
        } else {
            marketComment = String.format("📅 %s 기준 | ", timeframeDesc) + 
                           generateMarketComment(safetyRate, volatilityRate);
        }
        
        MarketSafetyInfo marketSafety = MarketSafetyInfo.builder()
                .totalStocks(totalCount)
                .safeStocks(probabilitySafeCount) // 확률 기반 개수 사용
                .riskyStocks(totalCount - probabilitySafeCount)
                .safetyRate(safetyRate * 100)
                .lowVolatilityStocks(lowVolCount)
                .highVolatilityStocks(totalCount - lowVolCount)
                .volatilityRate(volatilityRate * 100)
                .marketComment(marketComment)
                .build();
        
        return ChatResponse.builder()
                .message(null) // 대시보드 모드: 메시지 없음
                .type("recommendation_dashboard") // 새로운 타입
                .recommendations(recommendations)
                .chartData(chartDataMap)
                .marketSafety(marketSafety)
                .build();
    }
    
    /**
     * 특정 종목 분석 응답
     */
    private ChatResponse handleStockAnalysis(String ticker, String message) {
        // 타임프레임 감지
        String timeframe = detectTimeframe(message);
        PredictionResponse timeframeData = predictionService.getPredictionsByTimeframe(timeframe);
        
        log.info("📅 감지된 타임프레임: {}", timeframe);
        
        StockPrediction stock = timeframeData.getPredictions().get(ticker);
        
        if (stock == null) {
            return ChatResponse.builder()
                    .message("😢 해당 종목의 예측 데이터를 찾을 수 없습니다.")
                    .type("error")
                    .build();
        }
        
        // 타임프레임 설명
        String timeframeDesc;
        switch (timeframe) {
            case "1day": timeframeDesc = "내일"; break;
            case "3day": timeframeDesc = "3일 후"; break;
            case "10day": timeframeDesc = "10일 후"; break;
            default: timeframeDesc = "이번 주"; break;
        }
        
        // 상승 확률 계산
        double upwardProbability;
        if (stock.getDirection().getPrediction() == 1) {
            upwardProbability = stock.getDirection().getProbability() * 100;
        } else {
            upwardProbability = (1 - stock.getDirection().getProbability()) * 100;
        }
        
        // 레이블 생성 (확률 기반)
        String riskLabel = stock.getRisk().getPrediction() == 0 ? "안전" : "위험";
        String volatilityLabel = stock.getVolatility().getPrediction() == 0 ? "낮음" : "높음";
        
        String analysisMessage = String.format(
                "🔍 **%s** (%s) 상세 분석\n" +
                "📅 예측 기간: %s\n\n" +
                "📊 현재가: %s원\n\n" +
                "📈 예측 결과:\n" +
                "• 위험도: %s (%.1f%%)\n" +
                "• 변동성: %s (%.1f%%)\n" +
                "• 방향성: 상승 %.1f%% | 하락 %.1f%%\n\n" +
                "💡 종합 의견: %s",
                stock.getStockName(),
                stock.getTicker(),
                timeframeDesc,
                currencyFormat.format(stock.getCurrentPrice().longValue()),
                riskLabel, stock.getRisk().getProbability() * 100,
                volatilityLabel, stock.getVolatility().getProbability() * 100,
                upwardProbability, 100 - upwardProbability,
                generateOverallOpinion(stock)
        );
        
        return ChatResponse.builder()
                .message(analysisMessage)
                .type("analysis")
                .build();
    }
    
    /**
     * 기본 응답 (개선 - 더 상세한 도움말)
     */
    private ChatResponse handleDefault() {
        // 현재 시장 안전도 가져오기
        double safetyRate = calculateProbabilityBasedSafetyRate();
        String date = predictionService.getPredictionDate();
        
        String message = String.format(
                "😊 **무엇을 도와드릴까요?**\n\n" +
                "📅 오늘 날짜: %s\n" +
                "🛡️ 시장 안전도: %.1f%%\n\n" +
                "💡 **사용 예시:**\n\n" +
                "**1. 투자 추천 받기**\n" +
                "• \"100만원 추천해줘\"\n" +
                "• \"500만원 안전하게\"\n" +
                "• \"백만원 좋은 종목 알려줘\"\n" +
                "• \"추천\" (금액 없으면 100만원 기본)\n\n" +
                "**2. 시장 상태 확인**\n" +
                "• \"시장 어때?\"\n" +
                "• \"오늘 상황은?\"\n" +
                "• \"지금 상태\"\n\n" +
                "**3. 종목 분석**\n" +
                "• \"삼성전자 분석해줘\"\n" +
                "• \"네이버 어때?\"\n" +
                "• \"카카오 내일 어떨까?\"\n\n" +
                "**4. 타임프레임 선택**\n" +
                "• 헤더 버튼 클릭 (내일/3일/5일/10일)\n" +
                "• 또는 메시지에 포함: \"내일\", \"3일 후\", \"10일 후\"\n\n" +
                "**💬 자연스럽게 물어보세요!**\n" +
                "\"뭐 살까?\", \"좋은 종목 없어?\", \"안전한 거 알려줘\" 등\n" +
                "어떤 표현이든 이해할 수 있습니다 😊",
                date, safetyRate * 100
        );
        
        return ChatResponse.builder()
                .message(message)
                .type("default")
                .build();
    }
    
    /**
     * 시장 상태 코멘트 생성
     */
    private String generateMarketComment(double safetyRate, double volatilityRate) {
        // 위험도와 변동성을 모두 고려한 코멘트
        if (safetyRate >= 0.5 && volatilityRate >= 0.5) {
            return "✅ 시장 안전 및 변동성 낮음: '안전한 낚시터'를 찾기 좋은 환경입니다. 아래 추천 목록을 확인해보세요.";
        } else if (safetyRate >= 0.3 && volatilityRate >= 0.3) {
            return "⚡ 시장 보통 수준: 신중한 종목 선택이 필요합니다. 추천 종목 중 상승 확률이 높은 것을 선택하세요.";
        } else if (safetyRate < 0.2 && volatilityRate < 0.2) {
            return "⚠️ 시장 위험 및 변동성 높음: '안전한 낚시터' 찾기 어려움. 오늘은 관망하거나 보수적인 접근을 권장합니다.";
        } else if (safetyRate < 0.3) {
            return "⚠️ 시장 위험도 높음: 안전한 종목이 부족합니다. 상대적으로 안전한 종목만 추천됩니다.";
        } else if (volatilityRate < 0.3) {
            return "📈 시장 변동성 높음: 가격 변동이 큽니다. 단기 투자 시 주의가 필요합니다.";
        } else {
            return "💡 현재 시장 상황을 고려하여 신중하게 투자하세요.";
        }
    }
    
    /**
     * 추천 이유 생성
     */
    private String generateReason(StockPrediction stock) {
        return String.format("안전(위험도 낮음), 저변동성, 상승 기대 %.1f%%",
                stock.getDirection().getProbability() * 100);
    }
    
    /**
     * 종합 의견 생성
     */
    private String generateOverallOpinion(StockPrediction stock) {
        if (stock.isSafeAndUpward()) {
            return "✅ 안전하면서 상승 기대되는 종목입니다. 투자 추천!";
        } else if (stock.isSafe()) {
            return "⚠️ 안전하지만 상승 기대는 낮습니다. 안정적 투자에 적합.";
        } else if (stock.isUpward()) {
            return "⚠️ 상승 기대는 있으나 위험도가 높습니다. 신중한 투자 필요.";
        } else {
            return "❌ 현재 투자 추천하지 않습니다.";
        }
    }
    
    /**
     * 확률 기반 안전도 계산
     * prediction=1이어도 probability를 기반으로 상대적 안전도 계산
     */
    private double calculateProbabilityBasedSafetyRate() {
        PredictionResponse predictions = predictionService.getAllPredictions();
        if (predictions == null || predictions.getPredictions() == null) {
            return 0.0;
        }
        
        // 각 종목의 안전 확률(1 - risk.probability)의 평균 계산
        double totalSafetyProb = predictions.getPredictions().values().stream()
                .mapToDouble(stock -> 1.0 - stock.getRisk().getProbability())
                .average()
                .orElse(0.0);
        
        return totalSafetyProb;
    }
    
    /**
     * 타임프레임 데이터에서 안전&상승 종목 필터링
     */
    private List<StockPrediction> getSafeAndUpwardStocksFromData(PredictionResponse data) {
        if (data == null || data.getPredictions() == null) {
            return java.util.Collections.emptyList();
        }
        return data.getPredictions().values().stream()
                .filter(stock -> stock.getRisk().getPrediction() == 0 
                        && stock.getVolatility().getPrediction() == 0 
                        && stock.getDirection().getPrediction() == 1)
                .sorted((a, b) -> Double.compare(
                        b.getDirection().getProbability(), 
                        a.getDirection().getProbability()
                ))
                .collect(java.util.stream.Collectors.toList());  // limit 제거
    }
    
    /**
     * 타임프레임 데이터에서 안전 종목 필터링
     */
    private List<StockPrediction> getSafeStocksFromData(PredictionResponse data) {
        if (data == null || data.getPredictions() == null) {
            return java.util.Collections.emptyList();
        }
        return data.getPredictions().values().stream()
                .filter(stock -> stock.getRisk().getPrediction() == 0 
                        && stock.getVolatility().getPrediction() == 0)
                .sorted((a, b) -> Double.compare(
                        a.getRisk().getProbability(), 
                        b.getRisk().getProbability()
                ))
                .collect(java.util.stream.Collectors.toList());  // limit 제거
    }
}

