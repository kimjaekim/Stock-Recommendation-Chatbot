package com.future.my.domain;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.Map;

/**
 * 챗봇 응답 데이터
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ChatResponse {
    
    /**
     * 응답 메시지
     */
    private String message;
    
    /**
     * 응답 타입 (greeting, recommendation, analysis, chart, error)
     */
    private String type;
    
    /**
     * 추천 종목 리스트
     */
    private List<StockRecommendation> recommendations;
    
    /**
     * 차트 이미지 데이터 (Base64) - 레거시
     */
    private List<ChartData> charts;
    
    /**
     * 시장 안전도 (0.0 ~ 1.0)
     */
    private Double marketSafetyRate;
    
    /**
     * Chart.js용 차트 데이터 맵
     * 키: 차트 타입 (marketSafety, recommendations, stockPrice 등)
     * 값: 차트 데이터 객체
     */
    private Map<String, Object> chartData;
    
    /**
     * 시장 안전도 상세 정보
     */
    private MarketSafetyInfo marketSafety;
}

