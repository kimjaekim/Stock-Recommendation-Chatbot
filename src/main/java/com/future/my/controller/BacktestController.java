package com.future.my.controller;

import com.future.my.service.BacktestService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * 백테스팅 API
 */
@RestController
@RequestMapping("/api/backtest")
public class BacktestController {
    private static final Logger log = LoggerFactory.getLogger(BacktestController.class);
    
    private final BacktestService backtestService;
    
    public BacktestController(BacktestService backtestService) {
        this.backtestService = backtestService;
    }
    
    /**
     * 백테스팅 결과 조회
     */
    @GetMapping
    public ResponseEntity<?> getBacktestResult() {
        try {
            log.info("백테스팅 결과 조회 요청");
            BacktestService.BacktestResult result = backtestService.generateBacktestResult();
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            log.error("백테스팅 결과 조회 실패", e);
            return ResponseEntity.internalServerError()
                    .body(java.util.Map.of("error", e.getMessage()));
        }
    }
}

