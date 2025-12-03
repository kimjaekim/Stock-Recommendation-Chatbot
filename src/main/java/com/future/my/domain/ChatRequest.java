package com.future.my.domain;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 챗봇 요청 데이터
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ChatRequest {
    
    /**
     * 사용자 메시지
     */
    private String message;
    
    /**
     * 세션 ID (선택사항)
     */
    private String sessionId;
}

