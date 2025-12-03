package com.future.my.domain;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

/**
 * 사용자 포트폴리오
 */
public class Portfolio {
    private List<PortfolioStock> stocks;
    private LocalDateTime lastUpdated;
    
    public Portfolio() {
        this.stocks = new ArrayList<>();
        this.lastUpdated = LocalDateTime.now();
    }
    
    // Getters and Setters
    public List<PortfolioStock> getStocks() {
        return stocks;
    }
    
    public void setStocks(List<PortfolioStock> stocks) {
        this.stocks = stocks;
    }
    
    public LocalDateTime getLastUpdated() {
        return lastUpdated;
    }
    
    public void setLastUpdated(LocalDateTime lastUpdated) {
        this.lastUpdated = lastUpdated;
    }
    
    // 포트폴리오에 주식 추가
    public void addStock(PortfolioStock stock) {
        this.stocks.add(stock);
        this.lastUpdated = LocalDateTime.now();
    }
    
    // 포트폴리오에서 주식 제거
    public void removeStock(String ticker) {
        this.stocks.removeIf(stock -> stock.getTicker().equals(ticker));
        this.lastUpdated = LocalDateTime.now();
    }
    
    // 총 투자금 계산
    public double getTotalInvestment() {
        return stocks.stream()
                .mapToDouble(stock -> stock.getPurchasePrice() * stock.getShares())
                .sum();
    }
    
    // 현재 평가액 계산
    public double getTotalValue() {
        return stocks.stream()
                .mapToDouble(stock -> stock.getCurrentPrice() * stock.getShares())
                .sum();
    }
    
    // 총 수익/손실 계산
    public double getTotalProfit() {
        return getTotalValue() - getTotalInvestment();
    }
    
    // 총 수익률 계산
    public double getTotalReturnRate() {
        double investment = getTotalInvestment();
        if (investment == 0) return 0;
        return (getTotalProfit() / investment) * 100;
    }
}

