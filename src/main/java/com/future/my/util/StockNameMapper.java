package com.future.my.util;

import java.util.HashMap;
import java.util.Map;

/**
 * 종목명 매핑 유틸리티
 * 티커 코드와 실제 종목명을 매핑
 */
public class StockNameMapper {
    
    private static final Map<String, String> STOCK_NAME_MAPPING = new HashMap<>();
    
    static {
        STOCK_NAME_MAPPING.put("005930.KS", "삼성전자");
        STOCK_NAME_MAPPING.put("000660.KS", "SK하이닉스");
        STOCK_NAME_MAPPING.put("051910.KS", "LG화학");
        STOCK_NAME_MAPPING.put("035420.KS", "NAVER");
        STOCK_NAME_MAPPING.put("035720.KS", "카카오");
        STOCK_NAME_MAPPING.put("005380.KS", "현대차");
        STOCK_NAME_MAPPING.put("000270.KS", "기아");
        STOCK_NAME_MAPPING.put("068270.KS", "셀트리온");
        STOCK_NAME_MAPPING.put("207940.KS", "삼성바이오로직스");
        STOCK_NAME_MAPPING.put("005490.KS", "POSCO");
        STOCK_NAME_MAPPING.put("006400.KS", "삼성SDI");
        STOCK_NAME_MAPPING.put("051900.KS", "LG생활건강");
        STOCK_NAME_MAPPING.put("028260.KS", "삼성물산");
        STOCK_NAME_MAPPING.put("012330.KS", "현대모비스");
        STOCK_NAME_MAPPING.put("066570.KS", "LG전자");
        STOCK_NAME_MAPPING.put("003550.KS", "LG");
        STOCK_NAME_MAPPING.put("096770.KS", "SK이노베이션");
        STOCK_NAME_MAPPING.put("017670.KS", "SK텔레콤");
        STOCK_NAME_MAPPING.put("009150.KS", "삼성전기");
        STOCK_NAME_MAPPING.put("034730.KS", "SK");
        STOCK_NAME_MAPPING.put("000720.KS", "현대건설");
        STOCK_NAME_MAPPING.put("003490.KS", "대한항공");
        STOCK_NAME_MAPPING.put("011200.KS", "HMM");
        STOCK_NAME_MAPPING.put("012450.KS", "한화에어로스페이스");
        STOCK_NAME_MAPPING.put("015760.KS", "한국전력");
        STOCK_NAME_MAPPING.put("016360.KS", "삼성생명");
        STOCK_NAME_MAPPING.put("017800.KS", "현대엘리베이");
        STOCK_NAME_MAPPING.put("018880.KS", "한온시스템");
        STOCK_NAME_MAPPING.put("020150.KS", "일동제약");
        STOCK_NAME_MAPPING.put("021240.KS", "코웨이");
    }
    
    /**
     * 티커 코드로 종목명 조회
     * @param ticker 티커 코드
     * @return 종목명 (없으면 티커 그대로 반환)
     */
    public static String getStockName(String ticker) {
        return STOCK_NAME_MAPPING.getOrDefault(ticker, ticker);
    }
    
    /**
     * 모든 종목명 매핑 반환
     * @return 종목명 매핑 Map
     */
    public static Map<String, String> getAllStockNames() {
        return new HashMap<>(STOCK_NAME_MAPPING);
    }
    
    /**
     * 종목명으로 티커 코드 조회 (역방향)
     * @param stockName 종목명
     * @return 티커 코드 (없으면 null)
     */
    public static String getTickerByName(String stockName) {
        return STOCK_NAME_MAPPING.entrySet().stream()
                .filter(entry -> entry.getValue().equals(stockName))
                .map(Map.Entry::getKey)
                .findFirst()
                .orElse(null);
    }
}

