package com.future.my.domain;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 종목 추천 정보
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class StockRecommendation {
    
    /**
     * 티커 코드
     */
    private String ticker;
    
    /**
     * 종목명
     */
    private String stockName;
    
    /**
     * 종목명 (프론트엔드용 별칭)
     */
    private String name;
    
    /**
     * 현재가
     */
    private Double currentPrice;
    
    /**
     * 투자 금액
     */
    private Double investmentAmount;
    
    /**
     * 매수 가능 주식 수
     */
    private Integer shares;
    
    /**
     * 실제 투자 금액 (주식 수 * 현재가)
     */
    private Double actualAmount;
    
    /**
     * 위험도 (0: 안전, 1: 위험)
     */
    private Integer risk;
    
    /**
     * 위험 확률 (0.0 ~ 1.0)
     */
    private Double riskProbability;
    
    /**
     * 변동성 (0: 낮음, 1: 높음)
     */
    private Integer volatility;
    
    /**
     * 변동성 확률 (0.0 ~ 1.0)
     */
    private Double volatilityProbability;
    
    /**
     * 방향성 (0: 하락, 1: 상승)
     */
    private Integer direction;
    
    /**
     * 방향성 상승 확률
     */
    private Double directionProbability;
    
    /**
     * 상승 기대 확률 (%)
     */
    private Double upwardProbability;
    
    /**
     * 추천 이유
     */
    private String reason;
}

