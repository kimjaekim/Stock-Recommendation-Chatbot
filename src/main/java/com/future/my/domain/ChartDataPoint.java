package com.future.my.domain;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 차트 데이터 포인트
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ChartDataPoint {
    
    /**
     * 레이블 (x축)
     */
    private String label;
    
    /**
     * 값 (y축)
     */
    private Double value;
    
    /**
     * 색상 (선택적)
     */
    private String color;
    
    /**
     * 추가 정보 (선택적)
     */
    private String info;
}

