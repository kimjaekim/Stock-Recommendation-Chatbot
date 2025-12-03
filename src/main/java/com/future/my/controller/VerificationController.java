package com.future.my.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.io.BufferedReader;
import java.io.File;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/verification")
@RequiredArgsConstructor
@Slf4j
public class VerificationController {

    private static final String PYTHON_PATH = "C:\\Windows\\py.exe";
    // 폴더 구조 변경: verify_today_predictions.py → analysis/verify_today_predictions.py
    private static final String VERIFY_SCRIPT_PATH = "C:\\tools\\spring_dev\\workspace_boot\\jusic_data\\analysis\\verify_today_predictions.py";
    private static final String WORKING_DIRECTORY = "C:\\tools\\spring_dev\\workspace_boot\\jusic_data";

    private final ObjectMapper objectMapper;

    @GetMapping("/today")
    public ResponseEntity<?> getTodayVerification() {
        log.info("GET /api/verification/today 요청 - 오늘의 예측 검증 시작");
        
        try {
            // Python 스크립트 실행
            ProcessBuilder pb = new ProcessBuilder(PYTHON_PATH, VERIFY_SCRIPT_PATH);
            pb.directory(new File(WORKING_DIRECTORY));
            pb.redirectErrorStream(true); // stderr도 stdout으로 병합
            
            log.debug("실행 명령: {} {}", PYTHON_PATH, VERIFY_SCRIPT_PATH);
            
            Process process = pb.start();
            
            // 출력 읽기
            String output;
            try (BufferedReader reader = new BufferedReader(
                    new InputStreamReader(process.getInputStream(), StandardCharsets.UTF_8))) {
                output = reader.lines().collect(Collectors.joining("\n"));
            }
            
            int exitCode = process.waitFor();
            log.debug("Python 스크립트 종료 코드: {}", exitCode);
            
            if (exitCode != 0) {
                log.error("Python 스크립트 실행 실패. 출력: {}", output);
                return ResponseEntity.internalServerError()
                        .body(Map.of("error", "검증 스크립트 실행 실패", "details", output));
            }
            
            // JSON 파싱
            Map<String, Object> results = objectMapper.readValue(output, Map.class);
            
            // recommendations 필드가 있는지 확인
            java.util.List<?> recommendations = (java.util.List<?>) results.get("recommendations");
            int recommendationCount = (recommendations != null) ? recommendations.size() : 0;
            
            log.info("✅ 검증 완료 - 정확도: {}%, 추천 종목: {}개, 평균 수익률: {}%", 
                    results.get("accuracy"), 
                    recommendationCount,
                    results.get("avg_return"));
            
            return ResponseEntity.ok(results);
            
        } catch (Exception e) {
            log.error("❌ 검증 API 오류: {}", e.getMessage(), e);
            return ResponseEntity.internalServerError()
                    .body(Map.of("error", "검증 중 오류 발생", "message", e.getMessage()));
        }
    }
}

