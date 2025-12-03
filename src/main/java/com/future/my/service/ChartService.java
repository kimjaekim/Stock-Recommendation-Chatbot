package com.future.my.service;

import com.future.my.domain.StockPrediction;
import lombok.extern.slf4j.Slf4j;
import org.jfree.chart.ChartFactory;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.plot.*;
import org.jfree.data.category.DefaultCategoryDataset;
import org.jfree.data.general.DefaultValueDataset;
import org.springframework.stereotype.Service;

import javax.imageio.ImageIO;
import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.util.Base64;
import java.util.List;

/**
 * 차트 생성 서비스
 */
@Slf4j
@Service
public class ChartService {
    
    private static final int CHART_WIDTH = 800;
    private static final int CHART_HEIGHT = 500;
    private static final int GAUGE_SIZE = 400;
    
    /**
     * 게이지 차트 생성 (시장 안전도) - 파이 차트로 대체
     * @param safetyRate 안전도 비율 (0.0 ~ 1.0)
     * @param safeCount 안전 종목 수
     * @param totalCount 전체 종목 수
     * @return Base64 인코딩된 이미지
     */
    public String createMarketSafetyGaugeChart(double safetyRate, int safeCount, int totalCount) {
        try {
            // 파이 차트 데이터셋 생성
            org.jfree.data.general.DefaultPieDataset dataset = new org.jfree.data.general.DefaultPieDataset();
            dataset.setValue("안전 종목", safeCount);
            dataset.setValue("위험 종목", totalCount - safeCount);
            
            // 차트 생성
            JFreeChart chart = ChartFactory.createPieChart(
                    String.format("시장 안전도: %.1f%%", safetyRate * 100),
                    dataset,
                    true,
                    true,
                    false
            );
            
            // 차트 스타일 설정
            chart.setBackgroundPaint(Color.WHITE);
            chart.getTitle().setFont(new Font("맑은 고딕", Font.BOLD, 24));
            
            // 파이 플롯 설정
            org.jfree.chart.plot.PiePlot plot = (org.jfree.chart.plot.PiePlot) chart.getPlot();
            plot.setBackgroundPaint(Color.WHITE);
            plot.setLabelFont(new Font("맑은 고딕", Font.PLAIN, 14));
            
            // 색상 설정
            plot.setSectionPaint("안전 종목", new Color(100, 255, 100));
            plot.setSectionPaint("위험 종목", new Color(255, 100, 100));
            
            // 이미지로 변환
            return chartToBase64(chart, GAUGE_SIZE, GAUGE_SIZE);
            
        } catch (Exception e) {
            log.error("게이지 차트 생성 실패", e);
            return null;
        }
    }
    
    /**
     * 막대 차트 생성 (종목별 상승 확률 비교)
     * @param stocks 종목 리스트
     * @return Base64 인코딩된 이미지
     */
    public String createStockComparisonBarChart(List<StockPrediction> stocks) {
        try {
            // 데이터셋 생성
            DefaultCategoryDataset dataset = new DefaultCategoryDataset();
            
            for (StockPrediction stock : stocks) {
                double probability = stock.getDirection().getProbability() * 100;
                dataset.addValue(probability, "상승 확률", stock.getStockName());
            }
            
            // 차트 생성
            JFreeChart chart = ChartFactory.createBarChart(
                    "추천 종목 상승 기대 확률 비교",
                    "종목",
                    "상승 확률 (%)",
                    dataset,
                    PlotOrientation.VERTICAL,
                    false,
                    true,
                    false
            );
            
            // 차트 스타일 설정
            chart.setBackgroundPaint(Color.WHITE);
            chart.getTitle().setFont(new Font("맑은 고딕", Font.BOLD, 20));
            
            CategoryPlot plot = chart.getCategoryPlot();
            plot.setBackgroundPaint(Color.WHITE);
            plot.setDomainGridlinePaint(Color.LIGHT_GRAY);
            plot.setRangeGridlinePaint(Color.LIGHT_GRAY);
            
            // 축 설정
            plot.getDomainAxis().setLabelFont(new Font("맑은 고딕", Font.PLAIN, 14));
            plot.getDomainAxis().setTickLabelFont(new Font("맑은 고딕", Font.PLAIN, 12));
            plot.getRangeAxis().setLabelFont(new Font("맑은 고딕", Font.PLAIN, 14));
            plot.getRangeAxis().setTickLabelFont(new Font("맑은 고딕", Font.PLAIN, 12));
            
            // 막대 색상 설정
            org.jfree.chart.renderer.category.BarRenderer renderer = 
                    (org.jfree.chart.renderer.category.BarRenderer) plot.getRenderer();
            renderer.setSeriesPaint(0, new Color(100, 150, 255));
            
            // 이미지로 변환
            return chartToBase64(chart, CHART_WIDTH, CHART_HEIGHT);
            
        } catch (Exception e) {
            log.error("막대 차트 생성 실패", e);
            return null;
        }
    }
    
    /**
     * 간단한 주가 라인 차트 생성 (캔들스틱 대신 간단한 버전)
     * @param stockName 종목명
     * @param ticker 티커
     * @return Base64 인코딩된 이미지
     */
    public String createSimpleStockChart(String stockName, String ticker) {
        try {
            // 실제로는 주가 데이터를 가져와야 하지만, 
            // 여기서는 간단한 플레이스홀더 차트를 생성
            
            DefaultCategoryDataset dataset = new DefaultCategoryDataset();
            dataset.addValue(100, "종가", "Day 1");
            dataset.addValue(105, "종가", "Day 2");
            dataset.addValue(103, "종가", "Day 3");
            dataset.addValue(108, "종가", "Day 4");
            dataset.addValue(110, "종가", "Day 5");
            
            JFreeChart chart = ChartFactory.createLineChart(
                    stockName + " (" + ticker + ") 주가 추이",
                    "날짜",
                    "가격",
                    dataset,
                    PlotOrientation.VERTICAL,
                    true,
                    true,
                    false
            );
            
            chart.setBackgroundPaint(Color.WHITE);
            chart.getTitle().setFont(new Font("맑은 고딕", Font.BOLD, 18));
            
            CategoryPlot plot = chart.getCategoryPlot();
            plot.setBackgroundPaint(Color.WHITE);
            plot.setDomainGridlinePaint(Color.LIGHT_GRAY);
            plot.setRangeGridlinePaint(Color.LIGHT_GRAY);
            
            return chartToBase64(chart, CHART_WIDTH, CHART_HEIGHT);
            
        } catch (Exception e) {
            log.error("주가 차트 생성 실패", e);
            return null;
        }
    }
    
    /**
     * JFreeChart를 Base64 인코딩된 PNG 이미지로 변환
     * @param chart JFreeChart 객체
     * @param width 너비
     * @param height 높이
     * @return Base64 인코딩된 이미지 문자열
     */
    private String chartToBase64(JFreeChart chart, int width, int height) throws IOException {
        BufferedImage image = chart.createBufferedImage(width, height);
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        ImageIO.write(image, "png", baos);
        byte[] imageBytes = baos.toByteArray();
        return "data:image/png;base64," + Base64.getEncoder().encodeToString(imageBytes);
    }
}

