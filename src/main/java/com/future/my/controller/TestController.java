package com.future.my.controller;

import com.future.my.domain.PredictionResponse;
import com.future.my.domain.StockPrediction;
import com.future.my.service.PredictionService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 테스트용 컨트롤러 (Phase 1 검증)
 */
@RestController
@RequestMapping("/api/test")
@RequiredArgsConstructor
public class TestController {
    
    private final PredictionService predictionService;
    
    /**
     * 전체 예측 데이터 조회
     */
    @GetMapping("/all")
    public PredictionResponse getAllPredictions() {
        return predictionService.getAllPredictions();
    }
    
    /**
     * 안전한 종목 조회
     */
    @GetMapping("/safe")
    public List<StockPrediction> getSafeStocks() {
        return predictionService.getSafeStocks();
    }
    
    /**
     * 안전&상승 종목 조회
     */
    @GetMapping("/safe-upward")
    public List<StockPrediction> getSafeAndUpwardStocks() {
        return predictionService.getSafeAndUpwardStocks();
    }
    
    /**
     * 시장 안전도 조회
     */
    @GetMapping("/market-safety")
    public Map<String, Object> getMarketSafety() {
        double safetyRate = predictionService.getMarketSafetyRate();
        Map<String, Object> result = new HashMap<>();
        result.put("date", predictionService.getPredictionDate());
        result.put("safetyRate", safetyRate);
        result.put("safetyPercentage", String.format("%.1f%%", safetyRate * 100));
        result.put("safeStockCount", predictionService.getSafeStocks().size());
        result.put("totalStockCount", predictionService.getAllPredictions().getTotalStocks());
        return result;
    }
}

