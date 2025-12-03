package com.future.my.domain;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 예측 상세 정보 (Direction, Volatility, Risk 공통)
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class PredictionDetail {
    
    /**
     * 예측 값 (0 또는 1)
     */
    private int prediction;
    
    /**
     * 예측 확률
     */
    private double probability;
    
    /**
     * 레이블 (예: "상승", "하락", "안전", "위험", "낮음", "높음")
     */
    private String label;
}

