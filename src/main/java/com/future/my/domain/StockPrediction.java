package com.future.my.domain;

import com.future.my.util.StockNameMapper;
import com.google.gson.annotations.SerializedName;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 주식 예측 데이터 모델
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class StockPrediction {
    
    /**
     * 티커 코드 (예: 005930.KS)
     */
    private String ticker;
    
    /**
     * 종목명
     */
    private String stockName;
    
    /**
     * 현재가
     */
    private Double currentPrice;
    
    /**
     * 방향성 예측 (상승/하락)
     */
    private PredictionDetail direction;
    
    /**
     * 변동성 예측 (낮음/높음)
     */
    private PredictionDetail volatility;
    
    /**
     * 위험도 예측 (안전/위험)
     */
    private PredictionDetail risk;
    
    /**
     * 종목명 (JSON에서 읽거나 계산)
     */
    public String getStockName() {
        return stockName != null ? stockName : StockNameMapper.getStockName(ticker);
    }
    
    /**
     * 안전한 종목 여부 (Risk=0 && Volatility=0)
     * @return 안전 여부
     */
    public boolean isSafe() {
        return risk != null && volatility != null 
                && risk.getPrediction() == 0 
                && volatility.getPrediction() == 0;
    }
    
    /**
     * 상승 기대 종목 여부 (Direction=1)
     * @return 상승 기대 여부
     */
    public boolean isUpward() {
        return direction != null && direction.getPrediction() == 1;
    }
    
    /**
     * 안전하면서 상승 기대 종목 여부
     * @return 안전&상승 여부
     */
    public boolean isSafeAndUpward() {
        return isSafe() && isUpward();
    }
}

