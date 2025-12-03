package com.future.my.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import com.future.my.domain.Portfolio;
import com.future.my.domain.PortfolioStock;
import com.future.my.domain.StockPrediction;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.io.File;
import java.io.IOException;
import java.time.LocalDateTime;

/**
 * 포트폴리오 관리 서비스
 */
@Service
public class PortfolioService {
    private static final Logger log = LoggerFactory.getLogger(PortfolioService.class);
    private static final String PORTFOLIO_FILE = "src/main/resources/data/portfolio.json";
    
    private final ObjectMapper mapper;
    private final PredictionService predictionService;
    
    public PortfolioService(PredictionService predictionService) {
        this.predictionService = predictionService;
        this.mapper = new ObjectMapper();
        this.mapper.registerModule(new JavaTimeModule());
    }
    
    /**
     * 포트폴리오 저장
     */
    public void savePortfolio(Portfolio portfolio) {
        try {
            File file = new File(PORTFOLIO_FILE);
            file.getParentFile().mkdirs();
            mapper.writerWithDefaultPrettyPrinter().writeValue(file, portfolio);
            log.info("포트폴리오 저장 완료: {} 종목", portfolio.getStocks().size());
        } catch (IOException e) {
            log.error("포트폴리오 저장 실패", e);
            throw new RuntimeException("포트폴리오 저장 실패", e);
        }
    }
    
    /**
     * 포트폴리오 불러오기
     */
    public Portfolio loadPortfolio() {
        try {
            File file = new File(PORTFOLIO_FILE);
            if (!file.exists()) {
                log.info("포트폴리오 파일 없음. 새로 생성");
                return new Portfolio();
            }
            Portfolio portfolio = mapper.readValue(file, Portfolio.class);
            
            // 현재가 업데이트
            updateCurrentPrices(portfolio);
            
            log.info("포트폴리오 불러오기 완료: {} 종목", portfolio.getStocks().size());
            return portfolio;
        } catch (IOException e) {
            log.error("포트폴리오 불러오기 실패", e);
            return new Portfolio();
        }
    }
    
    /**
     * 주식 추가
     */
    public Portfolio addStock(String ticker, String stockName, int shares, double purchasePrice, String memo) {
        Portfolio portfolio = loadPortfolio();
        
        PortfolioStock stock = new PortfolioStock(ticker, stockName, shares, purchasePrice);
        stock.setMemo(memo);
        stock.setPurchaseDate(LocalDateTime.now());
        
        // 현재가 설정
        StockPrediction prediction = predictionService.getAllPredictions()
                .getPredictions().get(ticker);
        if (prediction != null) {
            stock.setCurrentPrice(prediction.getCurrentPrice());
        }
        
        portfolio.addStock(stock);
        savePortfolio(portfolio);
        
        log.info("주식 추가: {} ({}주)", stockName, shares);
        return portfolio;
    }
    
    /**
     * 주식 제거
     */
    public Portfolio removeStock(String ticker) {
        Portfolio portfolio = loadPortfolio();
        portfolio.removeStock(ticker);
        savePortfolio(portfolio);
        
        log.info("주식 제거: {}", ticker);
        return portfolio;
    }
    
    /**
     * 포트폴리오 현재가 업데이트
     */
    private void updateCurrentPrices(Portfolio portfolio) {
        var predictions = predictionService.getAllPredictions().getPredictions();
        
        for (PortfolioStock stock : portfolio.getStocks()) {
            StockPrediction prediction = predictions.get(stock.getTicker());
            if (prediction != null) {
                stock.setCurrentPrice(prediction.getCurrentPrice());
            }
        }
    }
    
    /**
     * 포트폴리오와 예측 결합
     */
    public PortfolioWithPredictions getPortfolioWithPredictions() {
        Portfolio portfolio = loadPortfolio();
        var predictions = predictionService.getAllPredictions().getPredictions();
        
        PortfolioWithPredictions result = new PortfolioWithPredictions();
        result.setPortfolio(portfolio);
        
        for (PortfolioStock stock : portfolio.getStocks()) {
            StockPrediction prediction = predictions.get(stock.getTicker());
            if (prediction != null) {
                result.addPrediction(stock.getTicker(), prediction);
            }
        }
        
        return result;
    }
    
    /**
     * 포트폴리오와 예측을 함께 담는 DTO
     */
    public static class PortfolioWithPredictions {
        private Portfolio portfolio;
        private java.util.Map<String, StockPrediction> predictions = new java.util.HashMap<>();
        
        public Portfolio getPortfolio() {
            return portfolio;
        }
        
        public void setPortfolio(Portfolio portfolio) {
            this.portfolio = portfolio;
        }
        
        public java.util.Map<String, StockPrediction> getPredictions() {
            return predictions;
        }
        
        public void setPredictions(java.util.Map<String, StockPrediction> predictions) {
            this.predictions = predictions;
        }
        
        public void addPrediction(String ticker, StockPrediction prediction) {
            this.predictions.put(ticker, prediction);
        }
    }
}

