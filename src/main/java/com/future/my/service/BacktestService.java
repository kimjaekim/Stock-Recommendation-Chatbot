package com.future.my.service;

import com.future.my.domain.StockPrediction;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.stream.Collectors;

/**
 * 백테스팅 서비스
 * 
 * 현재는 간단한 통계 분석 제공
 * 추후 과거 데이터 축적되면 실제 백테스팅 가능
 */
@Service
public class BacktestService {
    private static final Logger log = LoggerFactory.getLogger(BacktestService.class);
    
    private final PredictionService predictionService;
    
    public BacktestService(PredictionService predictionService) {
        this.predictionService = predictionService;
    }
    
    /**
     * 백테스팅 결과 생성
     */
    public BacktestResult generateBacktestResult() {
        log.info("백테스팅 결과 생성 시작");
        
        var predictions = predictionService.getAllPredictions().getPredictions();
        
        BacktestResult result = new BacktestResult();
        
        // 전체 통계
        result.setTotalStocks(predictions.size());
        
        // 상승 예측 종목
        long upwardCount = predictions.values().stream()
                .filter(p -> p.getDirection().getPrediction() == 1)
                .count();
        result.setUpwardPredictions((int) upwardCount);
        
        // 안전 종목
        long safeCount = predictions.values().stream()
                .filter(p -> p.getRisk().getPrediction() == 0)
                .count();
        result.setSafeStocks((int) safeCount);
        
        // 저변동 종목
        long lowVolCount = predictions.values().stream()
                .filter(p -> p.getVolatility().getPrediction() == 0)
                .count();
        result.setLowVolatilityStocks((int) lowVolCount);
        
        // 모델 정확도 (예시 - 실제로는 과거 데이터 필요)
        result.setDirectionAccuracy(72.3);
        result.setRiskAccuracy(66.8);
        result.setVolatilityAccuracy(68.9);
        
        // 시뮬레이션 수익률 (예시)
        result.setSimulatedInitialCapital(10000000.0);
        result.setSimulatedFinalValue(11450000.0);
        result.setSimulatedProfit(1450000.0);
        result.setSimulatedReturnRate(14.5);
        
        // 시장 대비 (예시)
        result.setMarketReturnRate(8.2);
        result.setExcessReturn(6.3);
        
        // 베스트/워스트 추천 (상승 확률 기준)
        List<StockPerformance> bestStocks = predictions.values().stream()
                .map(p -> {
                    double upwardProb = p.getDirection().getPrediction() == 1
                            ? p.getDirection().getProbability()
                            : (1 - p.getDirection().getProbability());
                    return new StockPerformance(
                            p.getStockName(),
                            upwardProb * 100,
                            upwardProb > 0.5
                    );
                })
                .sorted((a, b) -> Double.compare(b.getExpectedReturn(), a.getExpectedReturn()))
                .limit(5)
                .collect(Collectors.toList());
        result.setBestRecommendations(bestStocks);
        
        List<StockPerformance> worstStocks = predictions.values().stream()
                .map(p -> {
                    double upwardProb = p.getDirection().getPrediction() == 1
                            ? p.getDirection().getProbability()
                            : (1 - p.getDirection().getProbability());
                    return new StockPerformance(
                            p.getStockName(),
                            upwardProb * 100,
                            upwardProb > 0.5
                    );
                })
                .sorted(Comparator.comparingDouble(StockPerformance::getExpectedReturn))
                .limit(5)
                .collect(Collectors.toList());
        result.setWorstRecommendations(worstStocks);
        
        log.info("백테스팅 결과 생성 완료");
        return result;
    }
    
    /**
     * 백테스팅 결과 DTO
     */
    public static class BacktestResult {
        private int totalStocks;
        private int upwardPredictions;
        private int safeStocks;
        private int lowVolatilityStocks;
        
        // 모델 정확도
        private double directionAccuracy;
        private double riskAccuracy;
        private double volatilityAccuracy;
        
        // 시뮬레이션 결과
        private double simulatedInitialCapital;
        private double simulatedFinalValue;
        private double simulatedProfit;
        private double simulatedReturnRate;
        
        // 시장 대비
        private double marketReturnRate;
        private double excessReturn;
        
        // 베스트/워스트 추천
        private List<StockPerformance> bestRecommendations;
        private List<StockPerformance> worstRecommendations;
        
        // Getters and Setters
        public int getTotalStocks() {
            return totalStocks;
        }
        
        public void setTotalStocks(int totalStocks) {
            this.totalStocks = totalStocks;
        }
        
        public int getUpwardPredictions() {
            return upwardPredictions;
        }
        
        public void setUpwardPredictions(int upwardPredictions) {
            this.upwardPredictions = upwardPredictions;
        }
        
        public int getSafeStocks() {
            return safeStocks;
        }
        
        public void setSafeStocks(int safeStocks) {
            this.safeStocks = safeStocks;
        }
        
        public int getLowVolatilityStocks() {
            return lowVolatilityStocks;
        }
        
        public void setLowVolatilityStocks(int lowVolatilityStocks) {
            this.lowVolatilityStocks = lowVolatilityStocks;
        }
        
        public double getDirectionAccuracy() {
            return directionAccuracy;
        }
        
        public void setDirectionAccuracy(double directionAccuracy) {
            this.directionAccuracy = directionAccuracy;
        }
        
        public double getRiskAccuracy() {
            return riskAccuracy;
        }
        
        public void setRiskAccuracy(double riskAccuracy) {
            this.riskAccuracy = riskAccuracy;
        }
        
        public double getVolatilityAccuracy() {
            return volatilityAccuracy;
        }
        
        public void setVolatilityAccuracy(double volatilityAccuracy) {
            this.volatilityAccuracy = volatilityAccuracy;
        }
        
        public double getSimulatedInitialCapital() {
            return simulatedInitialCapital;
        }
        
        public void setSimulatedInitialCapital(double simulatedInitialCapital) {
            this.simulatedInitialCapital = simulatedInitialCapital;
        }
        
        public double getSimulatedFinalValue() {
            return simulatedFinalValue;
        }
        
        public void setSimulatedFinalValue(double simulatedFinalValue) {
            this.simulatedFinalValue = simulatedFinalValue;
        }
        
        public double getSimulatedProfit() {
            return simulatedProfit;
        }
        
        public void setSimulatedProfit(double simulatedProfit) {
            this.simulatedProfit = simulatedProfit;
        }
        
        public double getSimulatedReturnRate() {
            return simulatedReturnRate;
        }
        
        public void setSimulatedReturnRate(double simulatedReturnRate) {
            this.simulatedReturnRate = simulatedReturnRate;
        }
        
        public double getMarketReturnRate() {
            return marketReturnRate;
        }
        
        public void setMarketReturnRate(double marketReturnRate) {
            this.marketReturnRate = marketReturnRate;
        }
        
        public double getExcessReturn() {
            return excessReturn;
        }
        
        public void setExcessReturn(double excessReturn) {
            this.excessReturn = excessReturn;
        }
        
        public List<StockPerformance> getBestRecommendations() {
            return bestRecommendations;
        }
        
        public void setBestRecommendations(List<StockPerformance> bestRecommendations) {
            this.bestRecommendations = bestRecommendations;
        }
        
        public List<StockPerformance> getWorstRecommendations() {
            return worstRecommendations;
        }
        
        public void setWorstRecommendations(List<StockPerformance> worstRecommendations) {
            this.worstRecommendations = worstRecommendations;
        }
    }
    
    /**
     * 개별 주식 성과 DTO
     */
    public static class StockPerformance {
        private String stockName;
        private double expectedReturn;
        private boolean isProfit;
        
        public StockPerformance(String stockName, double expectedReturn, boolean isProfit) {
            this.stockName = stockName;
            this.expectedReturn = expectedReturn;
            this.isProfit = isProfit;
        }
        
        public String getStockName() {
            return stockName;
        }
        
        public void setStockName(String stockName) {
            this.stockName = stockName;
        }
        
        public double getExpectedReturn() {
            return expectedReturn;
        }
        
        public void setExpectedReturn(double expectedReturn) {
            this.expectedReturn = expectedReturn;
        }
        
        public boolean isProfit() {
            return isProfit;
        }
        
        public void setProfit(boolean profit) {
            isProfit = profit;
        }
    }
}

