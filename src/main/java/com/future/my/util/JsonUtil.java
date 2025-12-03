package com.future.my.util;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.reflect.TypeToken;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Component;

import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.Reader;
import java.lang.reflect.Type;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.List;

/**
 * JSON 파일 읽기 유틸리티
 */
@Component
public class JsonUtil {
    
    private final Gson gson;
    
    public JsonUtil() {
        this.gson = new GsonBuilder()
                .setPrettyPrinting()
                .create();
    }
    
    /**
     * JSON 파일을 읽어서 객체 리스트로 변환
     * @param filePath 파일 경로 (classpath 기준)
     * @param clazz 변환할 클래스
     * @param <T> 타입
     * @return 객체 리스트
     * @throws IOException 파일 읽기 실패
     */
    public <T> List<T> readJsonListFromClasspath(String filePath, Class<T> clazz) throws IOException {
        ClassPathResource resource = new ClassPathResource(filePath);
        
        try (Reader reader = new InputStreamReader(resource.getInputStream(), StandardCharsets.UTF_8)) {
            Type listType = TypeToken.getParameterized(List.class, clazz).getType();
            return gson.fromJson(reader, listType);
        }
    }
    
    /**
     * JSON 파일을 읽어서 단일 객체로 변환
     * @param filePath 파일 경로 (classpath 기준)
     * @param clazz 변환할 클래스
     * @param <T> 타입
     * @return 객체
     * @throws IOException 파일 읽기 실패
     */
    public <T> T readJsonFromClasspath(String filePath, Class<T> clazz) throws IOException {
        ClassPathResource resource = new ClassPathResource(filePath);
        
        try (Reader reader = new InputStreamReader(resource.getInputStream(), StandardCharsets.UTF_8)) {
            return gson.fromJson(reader, clazz);
        }
    }
    
    /**
     * 객체를 JSON 문자열로 변환
     * @param object 변환할 객체
     * @return JSON 문자열
     */
    public String toJson(Object object) {
        return gson.toJson(object);
    }
    
    /**
     * 파일 시스템 경로에서 JSON 파일 읽기 (Python 스크립트가 생성한 파일용)
     * @param filePath 파일 시스템 경로 (절대 경로 또는 상대 경로)
     * @param clazz 변환할 클래스
     * @param <T> 타입
     * @return 객체
     * @throws IOException 파일 읽기 실패
     */
    public <T> T readJsonFromFile(String filePath, Class<T> clazz) throws IOException {
        File file = new File(filePath);
        try (Reader reader = Files.newBufferedReader(file.toPath(), StandardCharsets.UTF_8)) {
            return gson.fromJson(reader, clazz);
        }
    }
}

