package com.future.my.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;

/**
 * 멀티 타임프레임 챗봇 서비스
 * Python 챗봇과 연동
 */
@Slf4j
@Service
public class MultiTimeframeChatbotService {
    
    private final ObjectMapper objectMapper = new ObjectMapper();
    
    // Python 실행 경로 (환경에 맞게 수정)
    private static final String PYTHON_PATH = "py";
    
    // 챗봇 스크립트 경로 (폴더 구조 변경: core/chatbot_cli.py)
    private static final String CHATBOT_SCRIPT_PATH = "C:/tools/spring_dev/workspace_boot/jusic_data/core/chatbot_cli.py";
    
    /**
     * Python 챗봇 호출
     * @param userMessage 사용자 메시지
     * @return 챗봇 응답
     */
    public MultiTimeframeChatbotResponse chat(String userMessage) {
        try {
            log.info("🤖 멀티 타임프레임 챗봇 호출: {}", userMessage);
            
            // ProcessBuilder로 Python 실행
            ProcessBuilder processBuilder = new ProcessBuilder(
                PYTHON_PATH,
                CHATBOT_SCRIPT_PATH,
                userMessage
            );
            
            // 작업 디렉토리 설정 (절대 경로)
            processBuilder.directory(new java.io.File("C:/tools/spring_dev/workspace_boot/jusic_data"));
            
            // 프로세스 실행
            Process process = processBuilder.start();
            
            // stdout 읽기 (JSON 응답)
            BufferedReader reader = new BufferedReader(
                new InputStreamReader(process.getInputStream(), StandardCharsets.UTF_8)
            );
            
            StringBuilder output = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line);
            }
            
            // stderr 읽기 (로그)
            BufferedReader errorReader = new BufferedReader(
                new InputStreamReader(process.getErrorStream(), StandardCharsets.UTF_8)
            );
            StringBuilder errorOutput = new StringBuilder();
            while ((line = errorReader.readLine()) != null) {
                errorOutput.append(line).append("\n");
            }
            
            int exitCode = process.waitFor();
            
            if (exitCode != 0) {
                String errorMsg = errorOutput.toString();
                log.error("Python 스크립트 실행 실패 (exit code: {})", exitCode);
                log.error("stderr: {}", errorMsg);
                log.error("stdout: {}", output.toString());
                return MultiTimeframeChatbotResponse.error("챗봇 실행 실패: " + errorMsg);
            }
            
            log.info("Python 스크립트 실행 성공 (exit code: 0)");
            
            // JSON 파싱
            String jsonResponse = output.toString();
            log.debug("Python 응답: {}", jsonResponse);
            
            JsonNode jsonNode = objectMapper.readTree(jsonResponse);
            
            if (jsonNode.has("success") && jsonNode.get("success").asBoolean()) {
                String message = jsonNode.get("message").asText();
                String timeframe = jsonNode.get("timeframe").asText();
                
                MultiTimeframeChatbotResponse.MultiTimeframeChatbotResponseBuilder builder = 
                    MultiTimeframeChatbotResponse.builder()
                        .success(true)
                        .message(message)
                        .timeframe(timeframe);
                
                // 차트 데이터가 있으면 추가
                if (jsonNode.has("chartData")) {
                    builder.chartData(objectMapper.convertValue(
                        jsonNode.get("chartData"), 
                        java.util.Map.class
                    ));
                }
                
                // 추천 데이터가 있으면 추가
                if (jsonNode.has("recommendations")) {
                    builder.recommendations(objectMapper.convertValue(
                        jsonNode.get("recommendations"), 
                        java.util.List.class
                    ));
                }
                
                // 비교 데이터가 있으면 추가
                if (jsonNode.has("comparison")) {
                    builder.comparison(objectMapper.convertValue(
                        jsonNode.get("comparison"), 
                        java.util.Map.class
                    ));
                }
                
                return builder.build();
            } else {
                String error = jsonNode.get("error").asText();
                log.error("챗봇 에러: {}", error);
                return MultiTimeframeChatbotResponse.error(error);
            }
            
        } catch (Exception e) {
            log.error("챗봇 호출 중 오류 발생", e);
            return MultiTimeframeChatbotResponse.error("챗봇 오류: " + e.getMessage());
        }
    }
    
    /**
     * 챗봇 응답 DTO
     */
    @lombok.Data
    @lombok.Builder
    @lombok.NoArgsConstructor
    @lombok.AllArgsConstructor
    public static class MultiTimeframeChatbotResponse {
        private boolean success;
        private String message;
        private String timeframe;
        private String error;
        
        // 차트 데이터
        private java.util.Map<String, Object> chartData;
        
        // 추천 종목 리스트
        private java.util.List<java.util.Map<String, Object>> recommendations;
        
        // 비교 데이터
        private java.util.Map<String, Object> comparison;
        
        public static MultiTimeframeChatbotResponse error(String errorMessage) {
            return MultiTimeframeChatbotResponse.builder()
                .success(false)
                .error(errorMessage)
                .message("😢 죄송합니다. 챗봇 오류가 발생했습니다: " + errorMessage)
                .build();
        }
    }
}

