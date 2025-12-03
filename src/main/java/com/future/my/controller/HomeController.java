package com.future.my.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

/**
 * 홈 컨트롤러
 */
@Controller
public class HomeController {
    
    /**
     * 메인 페이지
     */
    @GetMapping("/")
    public String home() {
        return "forward:/index.html";
    }
}

