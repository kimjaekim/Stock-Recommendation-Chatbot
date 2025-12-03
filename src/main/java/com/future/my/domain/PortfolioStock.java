package com.future.my.domain;

import java.time.LocalDateTime;

/**
 * 포트폴리오 내 개별 주식
 */
public class PortfolioStock {
    private String ticker;
    private String stockName;
    private int shares;                  // 보유 주식 수
    private double purchasePrice;         // 매수가
    private LocalDateTime purchaseDate;   // 매수일
    private double currentPrice;          // 현재가
    private String memo;                  // 메모
    
    // Constructors
    public PortfolioStock() {
    }
    
    public PortfolioStock(String ticker, String stockName, int shares, double purchasePrice) {
        this.ticker = ticker;
        this.stockName = stockName;
        this.shares = shares;
        this.purchasePrice = purchasePrice;
        this.purchaseDate = LocalDateTime.now();
        this.currentPrice = purchasePrice;
    }
    
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
    
    public LocalDateTime getPurchaseDate() {
        return purchaseDate;
    }
    
    public void setPurchaseDate(LocalDateTime purchaseDate) {
        this.purchaseDate = purchaseDate;
    }
    
    public double getCurrentPrice() {
        return currentPrice;
    }
    
    public void setCurrentPrice(double currentPrice) {
        this.currentPrice = currentPrice;
    }
    
    public String getMemo() {
        return memo;
    }
    
    public void setMemo(String memo) {
        this.memo = memo;
    }
    
    // 수익/손실 계산
    public double getProfit() {
        return (currentPrice - purchasePrice) * shares;
    }
    
    // 수익률 계산
    public double getReturnRate() {
        if (purchasePrice == 0) return 0;
        return ((currentPrice - purchasePrice) / purchasePrice) * 100;
    }
    
    // 투자금 계산
    public double getTotalInvestment() {
        return purchasePrice * shares;
    }
    
    // 현재 평가액 계산
    public double getCurrentValue() {
        return currentPrice * shares;
    }
}

