package com.future.my.domain;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 시장 안전도 정보
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class MarketSafetyInfo {
    
    /**
     * 전체 종목 수
     */
    private Integer totalStocks;
    
    /**
     * 안전한 종목 수
     */
    private Integer safeStocks;
    
    /**
     * 안전도 비율 (%)
     */
    private Double safetyRate;
    
    /**
     * 위험 종목 수
     */
    private Integer riskyStocks;
    
    /**
     * 저변동성 종목 수 (Volatility=0)
     */
    private Integer lowVolatilityStocks;
    
    /**
     * 고변동성 종목 수 (Volatility=1)
     */
    private Integer highVolatilityStocks;
    
    /**
     * 변동성 안전도 (0.0 ~ 100.0)
     */
    private Double volatilityRate;
    
    /**
     * 시장 상태 코멘트
     */
    private String marketComment;
}

