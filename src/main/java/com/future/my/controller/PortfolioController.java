package com.future.my.controller;

import com.future.my.domain.Portfolio;
import com.future.my.service.PortfolioService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * 포트폴리오 관리 API
 */
@RestController
@RequestMapping("/api/portfolio")
public class PortfolioController {
    private static final Logger log = LoggerFactory.getLogger(PortfolioController.class);
    
    private final PortfolioService portfolioService;
    
    public PortfolioController(PortfolioService portfolioService) {
        this.portfolioService = portfolioService;
    }
    
    /**
     * 포트폴리오 조회 (예측 포함)
     */
    @GetMapping
    public ResponseEntity<?> getPortfolio() {
        try {
            log.info("포트폴리오 조회 요청");
            PortfolioService.PortfolioWithPredictions result = portfolioService.getPortfolioWithPredictions();
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            log.error("포트폴리오 조회 실패", e);
            return ResponseEntity.internalServerError()
                    .body(java.util.Map.of("error", e.getMessage()));
        }
    }
    
    /**
     * 주식 추가
     */
    @PostMapping("/add")
    public ResponseEntity<?> addStock(@RequestBody AddStockRequest request) {
        try {
            log.info("주식 추가 요청: {}", request.getStockName());
            
            Portfolio portfolio = portfolioService.addStock(
                    request.getTicker(),
                    request.getStockName(),
                    request.getShares(),
                    request.getPurchasePrice(),
                    request.getMemo()
            );
            
            return ResponseEntity.ok(java.util.Map.of(
                    "message", "주식 추가 완료",
                    "portfolio", portfolio
            ));
        } catch (Exception e) {
            log.error("주식 추가 실패", e);
            return ResponseEntity.internalServerError()
                    .body(java.util.Map.of("error", e.getMessage()));
        }
    }
    
    /**
     * 주식 제거
     */
    @DeleteMapping("/remove/{ticker}")
    public ResponseEntity<?> removeStock(@PathVariable String ticker) {
        try {
            log.info("주식 제거 요청: {}", ticker);
            
            Portfolio portfolio = portfolioService.removeStock(ticker);
            
            return ResponseEntity.ok(java.util.Map.of(
                    "message", "주식 제거 완료",
                    "portfolio", portfolio
            ));
        } catch (Exception e) {
            log.error("주식 제거 실패", e);
            return ResponseEntity.internalServerError()
                    .body(java.util.Map.of("error", e.getMessage()));
        }
    }
    
    /**
     * 포트폴리오 전체 삭제
     */
    @DeleteMapping("/clear")
    public ResponseEntity<?> clearPortfolio() {
        try {
            log.info("포트폴리오 전체 삭제 요청");
            
            Portfolio emptyPortfolio = new Portfolio();
            portfolioService.savePortfolio(emptyPortfolio);
            
            return ResponseEntity.ok(java.util.Map.of(
                    "message", "포트폴리오 전체 삭제 완료"
            ));
        } catch (Exception e) {
            log.error("포트폴리오 삭제 실패", e);
            return ResponseEntity.internalServerError()
                    .body(java.util.Map.of("error", e.getMessage()));
        }
    }
    
    /**
     * 주식 추가 요청 DTO
     */
    public static class AddStockRequest {
        private String ticker;
        private String stockName;
        private int shares;
        private double purchasePrice;
        private String memo;
        
        // Getters and Setters
        public String getTicker() {
            return ticker;
        }
        
        public void setTicker(String ticker) {
            this.ticker = ticker;
        }
        
        public String getStockName() {
            return stockName;
        }
        
        public void setStockName(String stockName) {
            this.stockName = stockName;
        }
        
        public int getShares() {
            return shares;
        }
        
        public void setShares(int shares) {
            this.shares = shares;
        }
        
        public double getPurchasePrice() {
            return purchasePrice;
        }
        
        public void setPurchasePrice(double purchasePrice) {
            this.purchasePrice = purchasePrice;
        }
        
        public String getMemo() {
            return memo;
        }
        
        public void setMemo(String memo) {
            this.memo = memo;
        }
    }
}

