package com.future.my.domain;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 차트 이미지 데이터
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ChartData {
    
    /**
     * 차트 타입 (gauge, bar, candlestick, line)
     */
    private String type;
    
    /**
     * 차트 제목
     */
    private String title;
    
    /**
     * 차트 이미지 (Base64 인코딩)
     */
    private String imageBase64;
    
    /**
     * 관련 티커 (종목 차트인 경우)
     */
    private String ticker;
    
    /**
     * 설명
     */
    private String description;
}

