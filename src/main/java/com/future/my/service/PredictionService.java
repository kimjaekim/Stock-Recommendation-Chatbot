package com.future.my.service;

import com.future.my.domain.PredictionResponse;
import com.future.my.domain.StockPrediction;
import com.future.my.util.JsonUtil;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import jakarta.annotation.PostConstruct;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * 예측 데이터 관리 서비스
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class PredictionService {
    
    private final JsonUtil jsonUtil;
    private PredictionResponse cachedPredictions; // 기본 (5day)
    private final Map<String, PredictionResponse> timeframeCache = new java.util.HashMap<>();
    
    /**
     * 서비스 초기화 시 예측 데이터 로드 (모든 타임프레임)
     */
    @PostConstruct
    public void init() {
        try {
            // 기본 5day 로드
            loadPredictions();
            log.info("✅ 예측 데이터 로드 성공: {} 종목", cachedPredictions.getTotalStocks());
            
            // 모든 타임프레임 로드
            loadTimeframePredictions("1day");
            loadTimeframePredictions("3day");
            loadTimeframePredictions("5day");
            loadTimeframePredictions("10day");
            
            log.info("✅ 멀티 타임프레임 데이터 로드 완료: {} 종류", timeframeCache.size());
        } catch (IOException e) {
            log.error("❌ 예측 데이터 로드 실패", e);
        }
    }
    
    // Python 스크립트가 생성한 예측 파일 경로 (폴더 구조 변경: predictions/)
    private static final String PREDICTIONS_DIR = "C:/tools/spring_dev/workspace_boot/jusic_data/predictions";
    
    /**
     * JSON 파일에서 예측 데이터 로드 (기본: 5day)
     * @throws IOException 파일 읽기 실패
     */
    public void loadPredictions() throws IOException {
        String filePath = PREDICTIONS_DIR + "/today_predictions_5day.json";
        this.cachedPredictions = jsonUtil.readJsonFromFile(
                filePath, 
                PredictionResponse.class
        );
        log.info("📊 예측 데이터 로드 완료: 날짜={}, 종목 수={}", 
                cachedPredictions.getDate(), 
                cachedPredictions.getTotalStocks());
    }
    
    /**
     * 타임프레임별 예측 데이터 로드
     * @param timeframe 타임프레임 (1day, 3day, 5day, 10day)
     * @throws IOException 파일 읽기 실패
     */
    public void loadTimeframePredictions(String timeframe) throws IOException {
        String filePath = PREDICTIONS_DIR + "/today_predictions_" + timeframe + ".json";
        PredictionResponse data = jsonUtil.readJsonFromFile(
                filePath, 
                PredictionResponse.class
        );
        timeframeCache.put(timeframe, data);
        log.info("📊 {} 데이터 로드: {} 종목", timeframe, data.getTotalStocks());
    }
    
    /**
     * 타임프레임별 예측 데이터 조회
     * @param timeframe 타임프레임 (1day, 3day, 5day, 10day)
     * @return 예측 응답
     */
    public PredictionResponse getPredictionsByTimeframe(String timeframe) {
        return timeframeCache.getOrDefault(timeframe, cachedPredictions);
    }
    
    /**
     * 전체 예측 데이터 조회
     * @return 예측 응답
     */
    public PredictionResponse getAllPredictions() {
        return cachedPredictions;
    }
    
    /**
     * 특정 티커의 예측 데이터 조회
     * @param ticker 티커 코드
     * @return 예측 데이터
     */
    public StockPrediction getPredictionByTicker(String ticker) {
        if (cachedPredictions == null || cachedPredictions.getPredictions() == null) {
            return null;
        }
        return cachedPredictions.getPredictions().get(ticker);
    }
    
    /**
     * 안전한 종목 필터링 (Risk=0 && Volatility=0)
     * @return 안전한 종목 리스트
     */
    public List<StockPrediction> getSafeStocks() {
        if (cachedPredictions == null || cachedPredictions.getPredictions() == null) {
            return List.of();
        }
        
        return cachedPredictions.getPredictions().values().stream()
                .filter(StockPrediction::isSafe)
                .collect(Collectors.toList());
    }
    
    /**
     * 안전하면서 상승 기대 종목 필터링 (Risk=0 && Volatility=0 && Direction=1)
     * @return 안전&상승 종목 리스트
     */
    public List<StockPrediction> getSafeAndUpwardStocks() {
        if (cachedPredictions == null || cachedPredictions.getPredictions() == null) {
            return List.of();
        }
        
        return cachedPredictions.getPredictions().values().stream()
                .filter(StockPrediction::isSafeAndUpward)
                .sorted((a, b) -> Double.compare(
                        b.getDirection().getProbability(), 
                        a.getDirection().getProbability()
                ))
                .collect(Collectors.toList());
    }
    
    /**
     * 시장 안전도 계산 (안전 종목 비율)
     * @return 안전 종목 비율 (0.0 ~ 1.0)
     */
    public double getMarketSafetyRate() {
        if (cachedPredictions == null || cachedPredictions.getPredictions() == null) {
            return 0.0;
        }
        
        long safeCount = cachedPredictions.getPredictions().values().stream()
                .filter(StockPrediction::isSafe)
                .count();
        
        return (double) safeCount / cachedPredictions.getTotalStocks();
    }
    
    /**
     * 저변동성 종목 수 조회
     * @return 저변동성 종목 수
     */
    public int getLowVolatilityStocksCount() {
        if (cachedPredictions == null || cachedPredictions.getPredictions() == null) {
            return 0;
        }
        
        return (int) cachedPredictions.getPredictions().values().stream()
                .filter(stock -> stock.getVolatility().getPrediction() == 0)
                .count();
    }
    
    /**
     * 시장 변동성 안전도 계산 (저변동성 종목 비율)
     * @return 저변동성 종목 비율 (0.0 ~ 1.0)
     */
    public double getMarketVolatilityRate() {
        if (cachedPredictions == null || cachedPredictions.getPredictions() == null) {
            return 0.0;
        }
        
        return (double) getLowVolatilityStocksCount() / cachedPredictions.getTotalStocks();
    }
    
    /**
     * 예측 날짜 조회
     * @return 예측 날짜
     */
    public String getPredictionDate() {
        return cachedPredictions != null ? cachedPredictions.getDate() : null;
    }
}

