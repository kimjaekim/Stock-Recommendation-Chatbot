package com.future.my.controller;

import com.future.my.domain.*;
import com.future.my.service.ChatbotService;
import com.future.my.service.ChartService;
import com.future.my.service.PredictionService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 챗봇 메인 컨트롤러
 */
@Slf4j
@RestController
@RequestMapping("/api/chat")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class ChatbotController {
    
    private final ChatbotService chatbotService;
    private final PredictionService predictionService;
    private final ChartService chartService;
    private final com.future.my.service.MultiTimeframeChatbotService multiTimeframeChatbotService;
    
    /**
     * 챗봇 메시지 처리
     */
    @PostMapping("/message")
    public ResponseEntity<ChatResponse> sendMessage(@RequestBody ChatRequest request) {
        log.info("💬 챗봇 요청: {}", request.getMessage());
        
        try {
            ChatResponse response = chatbotService.processMessage(request);
            
            // Chart.js로 전환 완료 - 레거시 JFreeChart 이미지 제거
            // chartData 필드로 데이터만 전송
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            log.error("챗봇 처리 중 오류 발생", e);
            return ResponseEntity.ok(ChatResponse.builder()
                    .message("😢 죄송합니다. 오류가 발생했습니다: " + e.getMessage())
                    .type("error")
                    .build());
        }
    }
    
    /**
     * 시장 안전도 조회 (듀얼 게이지용)
     */
    @GetMapping("/market-status")
    public ResponseEntity<Map<String, Object>> getMarketStatus() {
        PredictionResponse predictions = predictionService.getAllPredictions();
        
        // 방어 로직: predictions가 null이면 기본값 반환
        if (predictions == null || predictions.getPredictions() == null) {
            log.warn("⚠️ 예측 데이터가 없습니다. 기본값을 반환합니다.");
            Map<String, Object> result = new HashMap<>();
            result.put("date", predictionService.getPredictionDate());
            result.put("marketSafety", MarketSafetyInfo.builder()
                    .totalStocks(30)
                    .safeStocks(0)
                    .riskyStocks(30)
                    .safetyRate(0.0)
                    .lowVolatilityStocks(0)
                    .highVolatilityStocks(30)
                    .volatilityRate(0.0)
                    .marketComment("⚠️ 예측 데이터를 로드할 수 없습니다.")
                    .build());
            return ResponseEntity.ok(result);
        }
        
        int totalCount = predictions.getTotalStocks();
        String date = predictionService.getPredictionDate();
        
        // 확률 기반 안전도 계산
        double safetyRate = calculateProbabilityBasedSafetyRate();
        int probabilitySafeCount = (int) Math.round(safetyRate * totalCount);
        
        // 변동성 정보
        int lowVolCount = predictionService.getLowVolatilityStocksCount();
        double volatilityRate = (totalCount > 0) ? predictionService.getMarketVolatilityRate() : 0.0;
        
        // Infinity 방어: volatilityRate가 무한대이면 0으로 처리
        if (Double.isInfinite(volatilityRate) || Double.isNaN(volatilityRate)) {
            volatilityRate = 0.0;
        }
        
        // 시장 상태 코멘트 생성
        String marketComment = generateMarketComment(safetyRate, volatilityRate);
        
        MarketSafetyInfo marketSafety = MarketSafetyInfo.builder()
                .totalStocks(totalCount)
                .safeStocks(probabilitySafeCount)
                .riskyStocks(totalCount - probabilitySafeCount)
                .safetyRate(safetyRate * 100)
                .lowVolatilityStocks(lowVolCount)
                .highVolatilityStocks(totalCount - lowVolCount)
                .volatilityRate(volatilityRate * 100)
                .marketComment(marketComment)
                .build();
        
        Map<String, Object> result = new HashMap<>();
        result.put("date", date);
        result.put("marketSafety", marketSafety);
        
        log.info("📊 시장 상태: totalStocks={}, safeStocks={}, safetyRate={}%, volatilityRate={}%", 
                totalCount, probabilitySafeCount, 
                String.format("%.1f", safetyRate * 100), 
                String.format("%.1f", volatilityRate * 100));
        
        return ResponseEntity.ok(result);
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
     * 시장 상태 코멘트 생성
     */
    private String generateMarketComment(double safetyRate, double volatilityRate) {
        if (safetyRate >= 0.5 && volatilityRate >= 0.5) {
            return "✅ 시장 안전 및 변동성 낮음: '안전한 낚시터'를 찾기 좋은 환경입니다.";
        } else if (safetyRate >= 0.3 && volatilityRate >= 0.3) {
            return "⚡ 시장 보통 수준: 신중한 종목 선택이 필요합니다.";
        } else if (safetyRate < 0.2 && volatilityRate < 0.2) {
            return "⚠️ 시장 위험 및 변동성 높음: 오늘은 관망하거나 보수적인 접근을 권장합니다.";
        } else if (safetyRate < 0.3) {
            return "⚠️ 시장 위험도 높음: 상대적으로 안전한 종목만 추천됩니다.";
        } else if (volatilityRate < 0.3) {
            return "📈 시장 변동성 높음: 가격 변동이 큽니다. 단기 투자 시 주의가 필요합니다.";
        } else {
            return "💡 현재 시장 상황을 고려하여 신중하게 투자하세요.";
        }
    }
    
    /**
     * 안전한 종목 목록 조회
     */
    @GetMapping("/safe-stocks")
    public ResponseEntity<List<StockPrediction>> getSafeStocks() {
        List<StockPrediction> safeStocks = predictionService.getSafeStocks();
        return ResponseEntity.ok(safeStocks);
    }
    
    /**
     * 특정 종목 조회
     */
    @GetMapping("/stock/{ticker}")
    public ResponseEntity<StockPrediction> getStock(@PathVariable String ticker) {
        StockPrediction stock = predictionService.getPredictionByTicker(ticker);
        if (stock == null) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(stock);
    }
    
    /**
     * 종목 차트 조회
     */
    @GetMapping("/stock/{ticker}/chart")
    public ResponseEntity<Map<String, String>> getStockChart(@PathVariable String ticker) {
        StockPrediction stock = predictionService.getPredictionByTicker(ticker);
        if (stock == null) {
            return ResponseEntity.notFound().build();
        }
        
        String chartImage = chartService.createSimpleStockChart(stock.getStockName(), ticker);
        Map<String, String> result = new HashMap<>();
        result.put("ticker", ticker);
        result.put("stockName", stock.getStockName());
        result.put("chartImage", chartImage);
        
        return ResponseEntity.ok(result);
    }
    
    /**
     * 🆕 멀티 타임프레임 챗봇 (12개 모델)
     */
    @PostMapping("/multi-timeframe")
    public ResponseEntity<Map<String, Object>> multiTimeframeChat(@RequestBody ChatRequest request) {
        log.info("🚀 멀티 타임프레임 챗봇 요청: {}", request.getMessage());
        
        try {
            com.future.my.service.MultiTimeframeChatbotService.MultiTimeframeChatbotResponse response = 
                multiTimeframeChatbotService.chat(request.getMessage());
            
            Map<String, Object> result = new HashMap<>();
            result.put("success", response.isSuccess());
            result.put("message", response.getMessage());
            result.put("timeframe", response.getTimeframe());
            result.put("type", "multi_timeframe");
            
            // 차트 데이터가 있으면 추가
            if (response.getChartData() != null) {
                result.put("chartData", response.getChartData());
            }
            
            // 추천 데이터가 있으면 추가
            if (response.getRecommendations() != null) {
                result.put("recommendations", response.getRecommendations());
            }
            
            // 비교 데이터가 있으면 추가
            if (response.getComparison() != null) {
                result.put("comparison", response.getComparison());
            }
            
            if (!response.isSuccess()) {
                result.put("error", response.getError());
            }
            
            return ResponseEntity.ok(result);
            
        } catch (Exception e) {
            log.error("멀티 타임프레임 챗봇 처리 중 오류 발생", e);
            Map<String, Object> errorResult = new HashMap<>();
            errorResult.put("success", false);
            errorResult.put("message", "😢 죄송합니다. 오류가 발생했습니다: " + e.getMessage());
            errorResult.put("error", e.getMessage());
            return ResponseEntity.ok(errorResult);
        }
    }
}

