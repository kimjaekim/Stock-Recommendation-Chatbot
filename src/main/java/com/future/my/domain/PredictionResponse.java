package com.future.my.domain;

import com.google.gson.annotations.SerializedName;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Map;

/**
 * 전체 예측 응답 데이터
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class PredictionResponse {
    
    /**
     * 예측 날짜
     */
    private String date;
    
    /**
     * 타임스탬프
     */
    private String timestamp;
    
    /**
     * 전체 종목 수
     */
    private int totalStocks;
    
    /**
     * 종목별 예측 데이터 (티커 -> 예측 데이터)
     */
    private Map<String, StockPrediction> predictions;
}

