# PWA 아이콘 생성 가이드

## 필요한 아이콘:
- icon-192x192.png
- icon-512x512.png

## 옵션 1: 온라인 도구 사용 (추천)

### 🌐 PWA Image Generator
1. https://www.pwabuilder.com/imageGenerator 접속
2. "Upload an image" 클릭
3. 로고/이미지 업로드 (최소 512x512 권장)
4. "Generate" 클릭
5. 생성된 icon-192x192.png, icon-512x512.png 다운로드
6. `jusic/src/main/resources/static/` 폴더에 복사

### 🎨 Canva 사용
1. https://www.canva.com 접속
2. "Custom size" → 512 x 512 px
3. 텍스트 추가: "🌊 안전한 낚시터"
4. 배경색: #667eea (보라색 그라디언트)
5. 다운로드: PNG
6. 192x192 버전도 동일하게 생성

## 옵션 2: 간단한 HTML로 생성

아래 HTML을 브라우저에서 열고 우클릭 → "이미지로 저장":

```html
<!DOCTYPE html>
<html>
<head>
<style>
.icon {
    width: 512px;
    height: 512px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 80px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}
.icon-text {
    font-size: 200px;
    text-align: center;
}
</style>
</head>
<body>
<div class="icon">
    <div class="icon-text">🌊</div>
</div>
</body>
</html>
```

## 옵션 3: 임시로 favicon.ico 사용

현재 favicon.ico가 있다면 임시로 사용 가능:

```bash
# PowerShell에서 실행
Copy-Item favicon.ico icon-192x192.png
Copy-Item favicon.ico icon-512x512.png
```

## 📱 테스트 방법

1. Chrome 개발자 도구 (F12)
2. Application 탭
3. Manifest 확인
4. "Add to home screen" 테스트

## ✅ 완료 후 확인사항

- [ ] icon-192x192.png 파일 존재
- [ ] icon-512x512.png 파일 존재
- [ ] Chrome에서 "설치" 버튼 표시
- [ ] 모바일에서 홈 화면 추가 가능
