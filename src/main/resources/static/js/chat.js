// DOM 요소
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const loadingIndicator = document.getElementById('loadingIndicator');
const safeCount = document.getElementById('safeCount');
const totalCount = document.getElementById('totalCount');

// API 엔드포인트
const API_BASE_URL = '/api/chat';

// Chart 인스턴스 저장
let riskGaugeChart = null;
let volatilityGaugeChart = null;
let chartInstances = [];

// 전역 변수
let currentTimeframe = '5day'; // 기본값
let highProbabilityStocks = []; // 고확률 종목 저장

// 초기화
document.addEventListener('DOMContentLoaded', () => {
    loadMarketStatus();
    
    // 이벤트 리스너
    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});

/**
 * 시장 안전도 로드 및 게이지 차트 생성
 */
async function loadMarketStatus() {
    try {
        console.log('🔄 시장 안전도 로드 시작...');
        const response = await fetch(`${API_BASE_URL}/market-status`);
        const data = await response.json();
        console.log('📥 서버 응답 데이터:', JSON.stringify(data, null, 2));
        
        // marketSafety 객체가 있는지 확인
        if (data.marketSafety) {
            console.log('✅ marketSafety 객체 발견:', JSON.stringify(data.marketSafety, null, 2));
            updateMarketSafetyHeader(data.marketSafety);
        } else {
            console.warn('⚠️ marketSafety 객체 없음, 레거시 구조 사용');
            // 레거시 데이터 구조 지원
            const marketSafety = {
                safeStocks: data.safeStockCount || 0,
                totalStocks: data.totalStockCount || 30,
                lowVolatilityStocks: 0,
                safetyRate: (data.safetyRate || 0) * 100,
                volatilityRate: 0,
                marketComment: '💡 현재 시장 상황을 고려하여 신중하게 투자하세요.'
            };
            updateMarketSafetyHeader(marketSafety);
        }
        
    } catch (error) {
        console.error('❌ 시장 안전도 로드 실패:', error);
    }
}

/**
 * 듀얼 게이지 차트 생성 (Risk + Volatility)
 */
function createDualGaugeCharts(marketSafety) {
    console.log('📊 createDualGaugeCharts 호출:', JSON.stringify(marketSafety, null, 2));
    
    // 기본값 설정 (데이터가 없을 때 방어)
    const totalStocks = marketSafety.totalStocks || 30;
    const safeStocks = marketSafety.safeStocks || 0;
    const lowVolStocks = marketSafety.lowVolatilityStocks || 0;
    const safetyRate = marketSafety.safetyRate || 0;
    const volatilityRate = marketSafety.volatilityRate || 0;
    
    console.log('🔧 최종 값:', JSON.stringify({totalStocks, safeStocks, lowVolStocks, safetyRate, volatilityRate}, null, 2));
    
    // Risk 게이지 생성
    createGaugeChart(
        'riskGaugeChart',
        safeStocks,
        totalStocks,
        safetyRate,
        '안전',
        '위험'
    );
    
    // Volatility 게이지 생성
    createGaugeChart(
        'volatilityGaugeChart',
        lowVolStocks,
        totalStocks,
        volatilityRate,
        '저변동',
        '고변동'
    );
}

/**
 * 단일 게이지 차트 생성 (고품질)
 */
function createGaugeChart(canvasId, safeCount, total, rate, safeLabel, riskyLabel) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    
    // 방어 로직: total이 0이면 차트 생성하지 않음
    if (!total || total === 0) {
        console.warn(`⚠️ ${canvasId}: total이 0이므로 차트를 생성하지 않습니다.`);
        return;
    }
    
    // 기존 차트 제거
    if (canvasId === 'riskGaugeChart' && riskGaugeChart) {
        riskGaugeChart.destroy();
    } else if (canvasId === 'volatilityGaugeChart' && volatilityGaugeChart) {
        volatilityGaugeChart.destroy();
    }
    
    // rate 타입 확인 및 변환
    const rateValue = (typeof rate === 'number') ? rate : parseFloat(rate) || 0;
    const percentage = rateValue.toFixed(1);
    const riskyCount = total - safeCount;
    
    console.log(`📊 ${canvasId} 차트 생성:`, {safeCount, total, rate, rateValue, percentage, typeof_rate: typeof rate});
    
    // 색상 결정 (rateValue 기반)
    let safeColor, riskyColor;
    if (rateValue >= 50) {
        safeColor = '#4caf50'; // 초록
        riskyColor = '#e0e0e0'; // 회색
    } else if (rateValue >= 30) {
        safeColor = '#ff9800'; // 주황
        riskyColor = '#ffccbc'; // 연한 빨강
    } else {
        safeColor = '#f44336'; // 빨강
        riskyColor = '#ffebee'; // 매우 연한 빨강
    }
    
    // 고품질 차트 옵션
    const chartOptions = {
        devicePixelRatio: window.devicePixelRatio || 2, // 고해상도 렌더링
    };
    
    // 그라데이션 생성 (고품질)
    const safeGradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 250);
    safeGradient.addColorStop(0, safeColor);
    safeGradient.addColorStop(1, safeColor + 'cc'); // 약간 투명하게
    
    const riskyGradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 250);
    riskyGradient.addColorStop(0, riskyColor);
    riskyGradient.addColorStop(1, riskyColor + 'aa');
    
    const chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: [safeLabel, riskyLabel],
            datasets: [{
                data: [safeCount, riskyCount],
                backgroundColor: [safeGradient, riskyGradient],
                borderColor: 'rgba(255, 255, 255, 1)',
                borderWidth: 3,
                hoverOffset: 10,
                hoverBorderWidth: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            devicePixelRatio: window.devicePixelRatio || 2, // 고해상도
            cutout: '65%',
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom',
                    labels: {
                        font: {
                            size: 11,
                            weight: '600'
                        },
                        padding: 8,
                        usePointStyle: true,
                        pointStyle: 'circle',
                        generateLabels: function(chart) {
                            const data = chart.data;
                            return data.labels.map((label, i) => {
                                const value = data.datasets[0].data[i];
                                // 방어 로직: total이 0이거나 없으면 0%로 표시
                                const percent = (total && total > 0) ? (value / total * 100).toFixed(1) : '0.0';
                                return {
                                    text: `${label}: ${value}개 (${percent}%)`,
                                    fillStyle: data.datasets[0].backgroundColor[i],
                                    strokeStyle: '#fff',
                                    lineWidth: 2,
                                    hidden: false,
                                    index: i
                                };
                            });
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.9)',
                    titleFont: { size: 16, weight: 'bold' },
                    bodyFont: { size: 14 },
                    padding: 15,
                    cornerRadius: 10,
                    callbacks: {
                        label: function(context) {
                            const value = context.raw;
                            // 방어 로직: total이 0이거나 없으면 0%로 표시
                            const percent = (total && total > 0) ? (value / total * 100).toFixed(1) : '0.0';
                            return `${context.label}: ${value}개 (${percent}%)`;
                        }
                    }
                }
            },
            animation: {
                animateScale: true,
                animateRotate: true,
                duration: 1500,
                easing: 'easeInOutQuart'
            }
        },
        plugins: [{
            id: 'centerText',
            beforeDraw: function(chart) {
                const { ctx, width, height } = chart;
                ctx.restore();
                
                // 큰 % 숫자 (크기 축소!)
                const mainFontSize = Math.min(width, height) / 5.5; // 적당한 크기
                ctx.font = `800 ${mainFontSize}px 'Arial', sans-serif`;
                ctx.textBaseline = 'middle';
                ctx.textAlign = 'center';
                
                const text = `${percentage}%`;
                const textX = width / 2;
                const textY = height / 2 - 5;
                
                // 외곽선 효과 (테두리)
                ctx.strokeStyle = 'white';
                ctx.lineWidth = 5;
                ctx.strokeText(text, textX, textY);
                
                // 그라데이션 텍스트
                const gradient = ctx.createLinearGradient(0, textY - mainFontSize/2, 0, textY + mainFontSize/2);
                gradient.addColorStop(0, safeColor);
                gradient.addColorStop(1, safeColor + 'cc');
                ctx.fillStyle = gradient;
                ctx.shadowColor = 'rgba(0, 0, 0, 0.3)';
                ctx.shadowBlur = 10;
                ctx.fillText(text, textX, textY);
                
                // 작은 라벨 (하단) - 크기 축소
                ctx.shadowBlur = 0;
                ctx.font = `600 ${mainFontSize / 4}px 'Arial', sans-serif`;
                ctx.fillStyle = '#666';
                ctx.fillText(safeLabel, textX, textY + mainFontSize / 1.5);
                
                ctx.save();
            }
        }]
    });
    
    // 차트 인스턴스 저장
    if (canvasId === 'riskGaugeChart') {
        riskGaugeChart = chart;
    } else if (canvasId === 'volatilityGaugeChart') {
        volatilityGaugeChart = chart;
    }
    chartInstances.push(chart);
}

/**
 * 메시지 전송
 */
async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;
    
    // 타임프레임 키워드 추가
    const timeframeKeywords = {
        '1day': '내일',
        '3day': '3일 후',
        '5day': '',  // 기본값이므로 키워드 없음
        '10day': '10일 후'
    };
    
    // 메시지에 타임프레임 키워드가 없으면 추가
    let enhancedMessage = message;
    const hasTimeframe = message.includes('내일') || message.includes('3일') || 
                         message.includes('10일') || message.includes('장기');
    
    if (!hasTimeframe && currentTimeframe !== '5day') {
        enhancedMessage = `${timeframeKeywords[currentTimeframe]} ${message}`;
    }
    
    // 사용자 메시지 표시 (원본)
    addMessage('user', message);
    messageInput.value = '';
    
    // 전송 버튼 비활성화
    sendButton.disabled = true;
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/message`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: enhancedMessage,  // 타임프레임 키워드가 포함된 메시지
                sessionId: 'web-session-' + Date.now()
            })
        });
        
        const data = await response.json();
        
        console.log('📡 API 응답:', data.type);
        
        // 봇 응답 표시
        addBotResponse(data);
        
        // 고확률 종목 확인
        if (data.recommendations && data.recommendations.length > 0) {
            checkHighProbabilityStocks(data.recommendations);
        }
        
    } catch (error) {
        console.error('메시지 전송 실패:', error);
        addMessage('bot', '😢 죄송합니다. 오류가 발생했습니다. 다시 시도해주세요.');
    } finally {
        sendButton.disabled = false;
        showLoading(false);
    }
}

/**
 * 사용자 메시지 추가
 */
function addMessage(type, text) {
    // 첫 메시지가 전송되면 웰컴 카드 제거
    if (type === 'user') {
        const welcomeCard = document.querySelector('.welcome-card');
        if (welcomeCard) {
            welcomeCard.remove();
        }
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = type === 'user' ? '👤' : '🤖';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    
    const textDiv = document.createElement('div');
    textDiv.className = 'message-text';
    textDiv.innerHTML = formatMessage(text);
    
    content.appendChild(textDiv);
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

/**
 * 봇 응답 추가 - 대시보드 스타일
 */
function addBotResponse(response) {
    // 대시보드 모드: 메시지 없이 데이터만 표시
    if (response.type === 'recommendation_dashboard') {
        renderDashboard(response);
        return;
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = '🤖';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    
    // 메시지 텍스트 (있을 경우만)
    if (response.message) {
        const textDiv = document.createElement('div');
        textDiv.className = 'message-text';
        textDiv.innerHTML = formatMessage(response.message);
        content.appendChild(textDiv);
    }
    
    // Chart.js 차트 렌더링 (새로운 방식)
    if (response.chartData) {
        renderChartData(response.chartData, content);
    }
    
    // 추천 종목이 있으면 카드로 표시
    if (response.recommendations && response.recommendations.length > 0) {
        const cardsContainer = createStockCards(response.recommendations);
        content.appendChild(cardsContainer);
    }
    
    // 시장 안전도 정보 업데이트
    if (response.marketSafety) {
        updateMarketSafetyHeader(response.marketSafety);
    }
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

/**
 * 대시보드 모드 렌더링 (추천 요청 시)
 */
function renderDashboard(response) {
    // 기존 차트 인스턴스 파괴 (메모리 누수 방지)
    chartInstances.forEach(chart => chart.destroy());
    chartInstances.length = 0;
    
    // 웰컴 카드 제거
    const welcomeCard = document.querySelector('.welcome-card');
    if (welcomeCard) {
        welcomeCard.remove();
    }
    
    // 대시보드 컨테이너 생성
    const dashboardDiv = document.createElement('div');
    dashboardDiv.className = 'dashboard-container';
    
    // 1. 추천 비교 차트
    if (response.chartData && response.chartData.recommendations) {
        const comparisonChart = createBarChart(response.chartData.recommendations, '📈 추천 종목 상승 확률 비교');
        dashboardDiv.appendChild(comparisonChart);
    }
    
    // 2. 추천 종목 카드들 (파이 차트 없이)
    if (response.recommendations && response.recommendations.length > 0) {
        const cardsContainer = createDashboardStockCards(response.recommendations);
        dashboardDiv.appendChild(cardsContainer);
    }
    
    // 3. 시장 안전도 정보 업데이트
    if (response.marketSafety) {
        updateMarketSafetyHeader(response.marketSafety);
    }
    
    chatMessages.appendChild(dashboardDiv);
    scrollToBottom();
}

/**
 * Chart.js 차트 렌더링
 */
function renderChartData(chartData, container) {
    // 시장 안전도 차트
    if (chartData.marketSafety) {
        const marketChart = createDoughnutChart(chartData.marketSafety, '📊 시장 안전도');
        container.appendChild(marketChart);
    }
    
    // 추천 종목 비교 차트
    if (chartData.recommendations) {
        const recommendationsChart = createBarChart(chartData.recommendations, '📈 추천 종목 상승 확률 비교');
        container.appendChild(recommendationsChart);
    }
}

/**
 * 헤더의 시장 안전도 업데이트 (듀얼 게이지)
 */
function updateMarketSafetyHeader(marketSafety) {
    // 데이터 업데이트 (0/30 표시 제거)
    const safeCountEl = document.getElementById('safeCount');
    const lowVolCountEl = document.getElementById('lowVolCount');
    const marketCommentEl = document.getElementById('marketComment');
    
    if (safeCountEl) safeCountEl.textContent = marketSafety.safeStocks;
    if (lowVolCountEl) lowVolCountEl.textContent = marketSafety.lowVolatilityStocks || 0;
    if (marketCommentEl && marketSafety.marketComment) {
        marketCommentEl.textContent = marketSafety.marketComment;
    }
    
    // 듀얼 게이지 차트 업데이트
    createDualGaugeCharts(marketSafety);
}

/**
 * 도넛 차트 생성 - 화려한 그라데이션 버전
 */
function createDoughnutChart(data, title) {
    const chartContainer = document.createElement('div');
    chartContainer.className = 'chart-container-js';
    
    if (title) {
        const titleEl = document.createElement('h4');
        titleEl.className = 'chart-title';
        titleEl.innerHTML = title;
        chartContainer.appendChild(titleEl);
    }
    
    const canvasWrapper = document.createElement('div');
    canvasWrapper.className = 'chart-canvas-wrapper';
    canvasWrapper.style.height = '500px'; // 높이 증가
    canvasWrapper.style.position = 'relative';
    
    const canvas = document.createElement('canvas');
    const chartId = 'chart-' + Date.now() + '-' + Math.random();
    canvas.id = chartId;
    canvasWrapper.appendChild(canvas);
    chartContainer.appendChild(canvasWrapper);
    
    // 차트 생성 (비동기로 DOM에 추가된 후 렌더링)
    setTimeout(() => {
        const ctx = canvas.getContext('2d');
        
        // 그라데이션 배경 생성
        const safeGradient = ctx.createLinearGradient(0, 0, 0, 400);
        safeGradient.addColorStop(0, 'rgba(76, 175, 80, 1)');
        safeGradient.addColorStop(1, 'rgba(76, 175, 80, 0.7)');
        
        const riskyGradient = ctx.createLinearGradient(0, 0, 0, 400);
        riskyGradient.addColorStop(0, 'rgba(244, 67, 54, 1)');
        riskyGradient.addColorStop(1, 'rgba(244, 67, 54, 0.7)');
        
        const chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.values,
                    backgroundColor: [safeGradient, riskyGradient],
                    borderWidth: 4,
                    borderColor: '#ffffff',
                    hoverOffset: 15,
                    hoverBorderWidth: 5,
                    hoverBorderColor: '#667eea'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                devicePixelRatio: window.devicePixelRatio || 2, // 고해상도
                cutout: '65%',
                plugins: {
                    legend: {
                        display: true,
                        position: 'bottom',
                            labels: {
                                font: {
                                    size: 18, // 범례 폰트 크기 증가
                                    weight: 'bold'
                                },
                                padding: 25,
                            usePointStyle: true,
                            pointStyle: 'circle',
                            color: '#2c3e50',
                            generateLabels: function(chart) {
                                const data = chart.data;
                                return data.labels.map((label, i) => {
                                    const value = data.datasets[0].data[i];
                                    return {
                                        text: `${label}: ${value}개`,
                                        fillStyle: data.datasets[0].backgroundColor[i],
                                        strokeStyle: '#fff',
                                        lineWidth: 2,
                                        hidden: false,
                                        index: i
                                    };
                                });
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.85)',
                        titleFont: { 
                            size: 20, // 툴팁 폰트 크기 증가
                            weight: 'bold'
                        },
                        bodyFont: { 
                            size: 18 // 툴팁 폰트 크기 증가
                        },
                        padding: 20,
                        cornerRadius: 14,
                        displayColors: true,
                        boxPadding: 8,
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ${value}개 (${percentage}%)`;
                            },
                            afterLabel: function(context) {
                                if (context.label === '안전') {
                                    return '✅ 투자 가능 종목';
                                } else {
                                    return '⚠️ 투자 주의 종목';
                                }
                            }
                        }
                    }
                },
                animation: {
                    animateScale: true,
                    animateRotate: true,
                    duration: 1800,
                    easing: 'easeInOutQuart'
                }
            }
        });
        chartInstances.push(chart);
        
        // 중앙에 총 개수 표시
        const totalValue = data.values.reduce((a, b) => a + b, 0);
        const centerTextDiv = document.createElement('div');
        centerTextDiv.className = 'chart-center-text-large';
        centerTextDiv.innerHTML = `
            <div style="font-size: 48px; font-weight: 800; color: #667eea; margin-bottom: 8px;">${totalValue}</div>
            <div style="font-size: 18px; color: #666; font-weight: bold;">총 종목 수</div>
        `;
        centerTextDiv.style.position = 'absolute';
        centerTextDiv.style.top = '50%';
        centerTextDiv.style.left = '50%';
        centerTextDiv.style.transform = 'translate(-50%, -50%)';
        centerTextDiv.style.textAlign = 'center';
        centerTextDiv.style.pointerEvents = 'none';
        canvasWrapper.appendChild(centerTextDiv);
        
    }, 100);
    
    return chartContainer;
}

/**
 * 막대 차트 생성 (수평) - 화려한 그라데이션 버전
 */
function createBarChart(data, title) {
    const chartContainer = document.createElement('div');
    chartContainer.className = 'chart-container-js';
    
    if (title) {
        const titleEl = document.createElement('h4');
        titleEl.className = 'chart-title';
        titleEl.innerHTML = title;
        chartContainer.appendChild(titleEl);
    }
    
    const canvasWrapper = document.createElement('div');
    canvasWrapper.className = 'chart-canvas-wrapper';
    const chartHeight = Math.max(450, data.labels.length * 90); // 높이 증가
    canvasWrapper.style.height = chartHeight + 'px';
    
    const canvas = document.createElement('canvas');
    const chartId = 'chart-' + Date.now() + '-' + Math.random();
    canvas.id = chartId;
    canvasWrapper.appendChild(canvas);
    chartContainer.appendChild(canvasWrapper);
    
    // 차트 생성 (비동기)
    setTimeout(() => {
        const ctx = canvas.getContext('2d');
        
        // 그라데이션 배경 생성
        const gradients = data.values.map((value, index) => {
            const gradient = ctx.createLinearGradient(0, 0, ctx.canvas.width, 0);
            const color = data.colors[index];
            
            if (value >= 60) {
                gradient.addColorStop(0, 'rgba(76, 175, 80, 0.8)');
                gradient.addColorStop(1, 'rgba(76, 175, 80, 1)');
            } else if (value >= 50) {
                gradient.addColorStop(0, 'rgba(255, 152, 0, 0.8)');
                gradient.addColorStop(1, 'rgba(255, 152, 0, 1)');
            } else {
                gradient.addColorStop(0, 'rgba(244, 67, 54, 0.7)');
                gradient.addColorStop(1, 'rgba(244, 67, 54, 1)');
            }
            
            return gradient;
        });
        
            const chart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: '상승 확률',
                        data: data.values,
                        backgroundColor: gradients,
                        borderColor: data.colors,
                        borderWidth: 2,
                        borderRadius: 12,
                        barThickness: 45,
                        borderSkipped: false
                    }]
                },
                options: {
                    indexAxis: 'y',  // 수평 막대
                    responsive: true,
                    maintainAspectRatio: false,
                    devicePixelRatio: window.devicePixelRatio || 2, // 고해상도
                layout: {
                    padding: {
                        left: 10,
                        right: 30,
                        top: 10,
                        bottom: 10
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.85)',
                        titleFont: { 
                            size: 18, // 툴팁 폰트 크기 증가
                            weight: 'bold'
                        },
                        bodyFont: { 
                            size: 16 // 툴팁 폰트 크기 증가
                        },
                        padding: 18,
                        cornerRadius: 12,
                        displayColors: true,
                        boxPadding: 8,
                        callbacks: {
                            label: function(context) {
                                const value = context.parsed.x.toFixed(1);
                                return '상승 확률: ' + value + '%';
                            },
                            afterLabel: function(context) {
                                const value = context.parsed.x;
                                if (value >= 60) {
                                    return '✨ 높은 상승 기대';
                                } else if (value >= 50) {
                                    return '⚡ 중간 상승 기대';
                                } else {
                                    return '⚠️ 낮은 상승 기대';
                                }
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            },
                            font: {
                                size: 16, // X축 폰트 크기 증가
                                weight: 'bold'
                            },
                            color: '#666'
                        },
                        grid: {
                            color: 'rgba(102, 126, 234, 0.1)',
                            lineWidth: 2
                        },
                        border: {
                            color: '#667eea',
                            width: 2
                        }
                    },
                    y: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            font: {
                                size: 18, // Y축 폰트 크기 증가
                                weight: 'bold'
                            },
                            color: '#2c3e50',
                            padding: 15
                        }
                    }
                },
                animation: {
                    duration: 1500,
                    easing: 'easeInOutQuart',
                    onProgress: function(animation) {
                        // 애니메이션 중 약간의 효과
                    },
                    onComplete: function() {
                        // 애니메이션 완료 후 효과
                    }
                }
            }
        });
        chartInstances.push(chart);
    }, 100);
    
    return chartContainer;
}

/**
 * 대시보드용 종목 카드 생성 (차트 없이 정보만)
 */
function createDashboardStockCards(recommendations) {
    const container = document.createElement('div');
    container.className = 'recommendation-cards-container';
    
    recommendations.forEach((stock, index) => {
        // 디버깅: 데이터 확인
        console.log(`종목 ${index + 1} (${stock.stockName}):`, {
            risk: stock.risk,
            volatility: stock.volatility,
            direction: stock.direction,
            upwardProbability: stock.upwardProbability
        });
        
        const card = document.createElement('div');
        let cardClass = 'recommendation-card dashboard-card';
        
        // 안전도에 따른 스타일
        if (stock.risk === 0 && stock.volatility === 0) {
            cardClass += ' safe';
        } else if (stock.risk === 1) {
            cardClass += ' risky';
        } else {
            cardClass += ' neutral';
        }
        card.className = cardClass;

        // 카드 헤더
        const stockHeader = document.createElement('div');
        stockHeader.className = 'stock-header';
        stockHeader.innerHTML = `
            <h4>${index + 1}. 📊 ${stock.stockName}</h4>
            <span class="ticker">(${stock.ticker})</span>
        `;
        card.appendChild(stockHeader);

        // 현재가
        const currentPrice = document.createElement('div');
        currentPrice.className = 'stock-current-price';
        currentPrice.textContent = `현재가: ${stock.currentPrice.toLocaleString()}원`;
        card.appendChild(currentPrice);

        // 상단: 3가지 예측 결과 + 상승 확률
        const topInfo = document.createElement('div');
        topInfo.style.display = 'flex';
        topInfo.style.justifyContent = 'space-between';
        topInfo.style.alignItems = 'center';
        topInfo.style.marginBottom = '12px';
        topInfo.style.padding = '10px';
        topInfo.style.background = 'rgba(102, 126, 234, 0.03)';
        topInfo.style.borderRadius = '10px';
        
        // 왼쪽: 3가지 예측 결과 (확률 포함)
        const predictionsDiv = document.createElement('div');
        predictionsDiv.style.display = 'flex';
        predictionsDiv.style.flexDirection = 'column';
        predictionsDiv.style.gap = '4px';
        
        // 위험도 (낮을수록 안전)
        const riskText = stock.risk === 0 ? '🛡️ 안전' : `⚠️ 위험`;
        const riskColor = stock.risk === 0 ? '#4caf50' : '#f44336';
        
        // 변동성 (낮을수록 안정)
        const volText = stock.volatility === 0 ? '📉 저변동' : '📈 고변동';
        const volColor = stock.volatility === 0 ? '#4caf50' : '#ff9800';
        
        // 방향성 (확률 기반 판단!)
        let dirText, dirColor;
        if (stock.direction === 1) {
            // 상승 예측
            dirText = '📈 상승';
            dirColor = '#4caf50';
        } else {
            // 하락 예측이지만 확률 확인
            const dirProb = stock.directionProbability || 0.5;
            if (dirProb < 0.5) {
                // 하락 확률 < 50% → 실제로는 상승 가능성 높음!
                dirText = '📈 상승';
                dirColor = '#4caf50';
            } else {
                // 하락 확률 >= 50% → 진짜 하락
                dirText = '📉 하락';
                dirColor = '#f44336';
            }
        }
        
        predictionsDiv.innerHTML = `
            <div style="font-size: 11px; font-weight: 600; color: ${riskColor};">${riskText}</div>
            <div style="font-size: 11px; font-weight: 600; color: ${volColor};">${volText}</div>
            <div style="font-size: 11px; font-weight: 600; color: ${dirColor};">${dirText}</div>
        `;
        topInfo.appendChild(predictionsDiv);
        
        // 오른쪽: 상승 확률
        const probDiv = document.createElement('div');
        probDiv.style.textAlign = 'right';
        probDiv.innerHTML = `
            <div style="font-size: 24px; font-weight: 800; color: ${stock.upwardProbability >= 50 ? '#4caf50' : '#f44336'};">
                ${stock.upwardProbability.toFixed(1)}%
            </div>
            <div style="font-size: 10px; color: #999; font-weight: 600;">상승 기대</div>
        `;
        topInfo.appendChild(probDiv);
        
        card.appendChild(topInfo);
        
        // 확률 프로그레스 바 추가
        const probabilityContainer = document.createElement('div');
        createProbabilityBar('상승 확률', stock.upwardProbability, probabilityContainer);
        card.appendChild(probabilityContainer);

        // 캔들스틱 차트 영역 (핵심!)
        const chartDiv = document.createElement('div');
        chartDiv.className = 'stock-candlestick-chart';
        const chartCanvas = document.createElement('canvas');
        const chartId = `candlestick-${stock.ticker}-${Date.now()}`;
        chartCanvas.id = chartId;
        chartDiv.appendChild(chartCanvas);
        card.appendChild(chartDiv);
        
        // 차트 렌더링 (비동기)
        setTimeout(() => createCandlestickChart(chartId, stock), 100);

        // 투자 정보 (간결하게)
        const investmentInfo = document.createElement('div');
        investmentInfo.className = 'stock-investment-info';
        investmentInfo.style.marginTop = '10px';
        investmentInfo.style.padding = '10px';
        investmentInfo.style.background = 'rgba(102, 126, 234, 0.05)';
        investmentInfo.style.borderRadius = '8px';
        investmentInfo.style.fontSize = '13px';
        investmentInfo.innerHTML = `
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span>💰 투자</span>
                <strong>${stock.investmentAmount.toLocaleString()}원</strong>
            </div>
            <div style="display: flex; justify-content: space-between; color: #666;">
                <span>매수 가능</span>
                <strong style="color: #667eea;">${stock.shares}주</strong>
            </div>
        `;
        card.appendChild(investmentInfo);

        // 위험 경고 배너 추가
        if (stock.risk === 1) {
            const warningBanner = document.createElement('div');
            warningBanner.style.marginTop = '10px';
            warningBanner.style.padding = '10px';
            warningBanner.style.background = 'linear-gradient(135deg, #ff5252 0%, #f44336 100%)';
            warningBanner.style.color = 'white';
            warningBanner.style.borderRadius = '8px';
            warningBanner.style.fontSize = '12px';
            warningBanner.style.fontWeight = 'bold';
            warningBanner.style.textAlign = 'center';
            warningBanner.style.border = '2px solid #c62828';
            warningBanner.style.boxShadow = '0 2px 8px rgba(244, 67, 54, 0.3)';
            warningBanner.innerHTML = `
                ⚠️ 위험 경고: 이 종목은 손실 위험이 높습니다 (${(stock.riskProbability * 100).toFixed(0)}%)!<br>
                <span style="font-size: 11px; opacity: 0.9;">소액 분산 투자를 강력히 권장합니다.</span>
            `;
            card.appendChild(warningBanner);
        } else if (stock.volatility === 1) {
            const cautionBanner = document.createElement('div');
            cautionBanner.style.marginTop = '10px';
            cautionBanner.style.padding = '10px';
            cautionBanner.style.background = 'linear-gradient(135deg, #ff9800 0%, #f57c00 100%)';
            cautionBanner.style.color = 'white';
            cautionBanner.style.borderRadius = '8px';
            cautionBanner.style.fontSize = '12px';
            cautionBanner.style.fontWeight = 'bold';
            cautionBanner.style.textAlign = 'center';
            cautionBanner.style.border = '2px solid #e65100';
            cautionBanner.style.boxShadow = '0 2px 8px rgba(255, 152, 0, 0.3)';
            cautionBanner.innerHTML = `
                💡 주의: 변동성이 높은 종목입니다 (${(stock.volatilityProbability * 100).toFixed(0)}%)!<br>
                <span style="font-size: 11px; opacity: 0.9;">단기 투자 시 주의가 필요합니다.</span>
            `;
            card.appendChild(cautionBanner);
        }

        container.appendChild(card);
    });
    
    return container;
}

/**
 * 추천 종목 카드 생성
 */
function createStockCards(recommendations) {
    const container = document.createElement('div');
    container.className = 'stock-cards-container';
    
    recommendations.forEach((stock, index) => {
        const card = document.createElement('div');
        card.className = 'stock-card';
        
        // 안전도에 따른 테두리 색상
        if (stock.risk <= 0.3) {
            card.style.borderLeftColor = '#4caf50';
        } else if (stock.risk <= 0.7) {
            card.style.borderLeftColor = '#ff9800';
        } else {
            card.style.borderLeftColor = '#f44336';
        }
        
        // 카드 헤더
        const header = document.createElement('div');
        header.className = 'stock-card-header';
        header.innerHTML = `
            <div>
                <div class="stock-name">📊 ${stock.name}</div>
                <div class="stock-ticker">${stock.ticker}</div>
            </div>
            <div class="stock-price">${formatPrice(stock.currentPrice)}원</div>
        `;
        card.appendChild(header);
        
        // 예측 정보
        const predictions = document.createElement('div');
        predictions.className = 'stock-predictions';
        
        // 상승/하락 확률
        const upwardProb = stock.upwardProbability || 50;
        const downwardProb = 100 - upwardProb;
        const probClass = upwardProb >= 50 ? 'prediction-safe' : 'prediction-risk';
        
        predictions.innerHTML = `
            <div class="prediction-item">
                <span class="prediction-label">📈 상승 기대</span>
                <span class="prediction-value ${probClass}">${upwardProb.toFixed(1)}%</span>
            </div>
            <div class="prediction-item">
                <span class="prediction-label">📉 하락 예상</span>
                <span class="prediction-value">${downwardProb.toFixed(1)}%</span>
            </div>
        `;
        
        if (stock.reason) {
            predictions.innerHTML += `
                <div class="prediction-item" style="margin-top: 10px;">
                    <span style="color: #666; font-size: 0.9em;">${stock.reason}</span>
                </div>
            `;
        }
        
        card.appendChild(predictions);
        
        // 미니 차트 컨테이너 (높이 고정)
        const chartWrapper = document.createElement('div');
        chartWrapper.className = 'chart-mini-wrapper';
        
        const chartCanvas = document.createElement('canvas');
        chartCanvas.className = 'chart-mini';
        chartCanvas.id = `stock-chart-${index}`;
        chartWrapper.appendChild(chartCanvas);
        card.appendChild(chartWrapper);
        
        // 투자 정보
        if (stock.investmentAmount) {
            const investInfo = document.createElement('div');
            investInfo.className = 'stock-investment-info';
            investInfo.innerHTML = `
                <div class="investment-amount">💰 투자 금액: ${formatPrice(stock.investmentAmount)}원</div>
                <div style="margin-top: 5px; color: #666;">
                    약 ${stock.shares || 0}주 매수 가능
                </div>
            `;
            card.appendChild(investInfo);
        }
        
        container.appendChild(card);
        
        // 차트 렌더링 (비동기)
        setTimeout(() => {
            createStockMiniChart(chartCanvas.id, stock);
        }, 100);
    });
    
    return container;
}

/**
 * 종목별 미니 차트 생성 - 세련된 도넛 차트
 */
function createStockMiniChart(canvasId, stock) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.error('Canvas not found:', canvasId);
        return;
    }
    
    const upwardProb = stock.upwardProbability || 50;
    const downwardProb = 100 - upwardProb;
    
    // 색상 결정 (그라데이션 느낌)
    let upwardColor, downwardColor;
    if (upwardProb >= 60) {
        upwardColor = {
            background: 'rgba(76, 175, 80, 0.9)',
            border: '#4caf50'
        };
    } else if (upwardProb >= 50) {
        upwardColor = {
            background: 'rgba(255, 152, 0, 0.9)',
            border: '#ff9800'
        };
    } else {
        upwardColor = {
            background: 'rgba(244, 67, 54, 0.6)',
            border: '#f44336'
        };
    }
    
    downwardColor = {
        background: 'rgba(200, 200, 200, 0.4)',
        border: '#ccc'
    };
    
            try {
                const ctx = canvas.getContext('2d');
                const chart = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: ['상승 확률', '하락 확률'],
                        datasets: [{
                            data: [upwardProb, downwardProb],
                            backgroundColor: [
                                upwardColor.background,
                                downwardColor.background
                            ],
                            borderColor: [
                                upwardColor.border,
                                downwardColor.border
                            ],
                            borderWidth: 3,
                            hoverOffset: 8
                        }]
                    },
                    options: {
                        responsive: false,
                        maintainAspectRatio: false,
                        devicePixelRatio: window.devicePixelRatio || 2, // 고해상도
                        cutout: '65%',
                plugins: {
                    legend: {
                        display: true,
                        position: 'bottom',
                        labels: {
                            font: {
                                size: 11,
                                weight: 'bold'
                            },
                            padding: 10,
                            usePointStyle: true,
                            pointStyle: 'circle'
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.85)',
                        titleFont: {
                            size: 14,
                            weight: 'bold'
                        },
                        bodyFont: {
                            size: 13
                        },
                        padding: 12,
                        cornerRadius: 8,
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed;
                                return label + ': ' + value.toFixed(1) + '%';
                            }
                        }
                    }
                },
                animation: {
                    animateScale: true,
                    animateRotate: true,
                    duration: 1200,
                    easing: 'easeOutQuart'
                }
            }
        });
        
        chartInstances.push(chart);
        
        // 중앙에 확률 표시 (Canvas 오버레이)
        addCenterText(canvas, upwardProb.toFixed(1) + '%', upwardColor.border);
        
    } catch (error) {
        console.error('Chart creation error:', error);
    }
}

/**
 * 도넛 차트 중앙에 텍스트 추가
 */
function addCenterText(canvas, text, color) {
    const parent = canvas.parentElement;
    
    // 기존 텍스트가 있으면 제거
    const existingText = parent.querySelector('.chart-center-text');
    if (existingText) {
        existingText.remove();
    }
    
    const centerText = document.createElement('div');
    centerText.className = 'chart-center-text';
    centerText.textContent = text;
    centerText.style.position = 'absolute';
    centerText.style.top = '50%';
    centerText.style.left = '50%';
    centerText.style.transform = 'translate(-50%, -50%)';
    centerText.style.fontSize = '28px'; // 중앙 텍스트 크기 증가
    centerText.style.fontWeight = 'bold';
    centerText.style.color = color;
    centerText.style.pointerEvents = 'none';
    
    parent.style.position = 'relative';
    parent.appendChild(centerText);
}

/**
 * 캔들스틱 차트 생성 (Chart.js Financial)
 */
function createCandlestickChart(canvasId, stock) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.error('Canvas not found:', canvasId);
        return;
    }
    
    // 더미 데이터 생성 (30일치)
    const data = generateDummyCandlestickData(30, stock.currentPrice);
    
    const ctx = canvas.getContext('2d');
    
    try {
        const chart = new Chart(ctx, {
            type: 'candlestick',
            data: {
                datasets: [{
                    label: stock.stockName,
                    data: data
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                devicePixelRatio: window.devicePixelRatio || 2, // 고해상도
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleFont: { size: 13, weight: 'bold' },
                        bodyFont: { size: 12 },
                        padding: 10,
                        cornerRadius: 8
                    }
                },
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'day',
                            displayFormats: {
                                day: 'MM/dd'
                            }
                        },
                        ticks: {
                            font: { size: 10 },
                            color: '#999',
                            maxRotation: 0
                        },
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        ticks: {
                            font: { size: 10 },
                            color: '#999',
                            callback: function(value) {
                                return value.toLocaleString() + '원';
                            }
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    }
                }
            }
        });
        
        chartInstances.push(chart);
    } catch (error) {
        console.error('Candlestick chart creation error:', error);
        // 에러 시 플레이스홀더 표시
        canvas.parentElement.innerHTML = `
            <div style="text-align: center; color: #999; padding: 20px;">
                <div style="font-size: 14px;">📊 주가 차트</div>
                <div style="font-size: 12px; margin-top: 5px;">최근 30일 추이</div>
            </div>
        `;
    }
}

/**
 * 더미 캔들스틱 데이터 생성
 */
function generateDummyCandlestickData(days, currentPrice) {
    const data = [];
    const today = new Date();
    let price = currentPrice * 0.9; // 30일 전 가격 (현재가의 90%)
    
    for (let i = days; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        
        // 랜덤 변동 (-3% ~ +3%)
        const change = (Math.random() - 0.5) * 0.06;
        price = price * (1 + change);
        
        const open = price;
        const close = open * (1 + (Math.random() - 0.5) * 0.04);
        const high = Math.max(open, close) * (1 + Math.random() * 0.02);
        const low = Math.min(open, close) * (1 - Math.random() * 0.02);
        
        data.push({
            x: date.getTime(),
            o: open,
            h: high,
            l: low,
            c: close
        });
        
        price = close;
    }
    
    return data;
}

/**
 * 메시지 포맷팅 (줄바꿈, 볼드 등)
 */
function formatMessage(text) {
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>');
}

/**
 * 가격 포맷팅
 */
function formatPrice(price) {
    if (!price) return '0';
    return price.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

/**
 * 로딩 인디케이터 표시/숨김
 */
function showLoading(show) {
    loadingIndicator.style.display = show ? 'block' : 'none';
}

/**
 * 스크롤을 맨 아래로
 */
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

/**
 * 타임프레임 선택
 */
function selectTimeframe(timeframe) {
    currentTimeframe = timeframe;
    
    // 버튼 활성화 상태 변경
    document.querySelectorAll('.tf-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-timeframe="${timeframe}"]`).classList.add('active');
    
    // 사용자에게 피드백
    const timeframeNames = {
        '1day': '내일',
        '3day': '3일 후',
        '5day': '이번 주',
        '10day': '10일 후'
    };
    
    console.log(`📅 타임프레임 변경: ${timeframeNames[timeframe]}`);
    
    // 메시지 입력창에 포커스
    messageInput.focus();
}

/**
 * 확률 프로그레스 바 생성
 */
function createProbabilityBar(label, probability, container) {
    const barHtml = `
        <div class="probability-bar-container">
            <div class="probability-label">
                <span>${label}</span>
                <span>${probability.toFixed(1)}%</span>
            </div>
            <div class="probability-bar">
                <div class="probability-fill ${getProbabilityClass(probability)}" 
                     style="width: ${probability}%">
                    <span class="probability-text">${probability.toFixed(1)}%</span>
                </div>
            </div>
        </div>
    `;
    
    container.innerHTML += barHtml;
}

/**
 * 확률에 따른 클래스 반환
 */
function getProbabilityClass(probability) {
    if (probability >= 60) return 'high';
    if (probability >= 50) return 'medium';
    return 'low';
}

/**
 * 고확률 종목 알림 확인 및 표시
 */
function checkHighProbabilityStocks(recommendations) {
    if (!recommendations || recommendations.length === 0) return;
    
    // 상승 확률 60% 이상 종목 필터링
    const highProb = recommendations.filter(rec => rec.upwardProbability >= 60);
    
    if (highProb.length > 0) {
        highProbabilityStocks = highProb;
        showAlertBadge(highProb);
    }
}

/**
 * 알림 배지 표시
 */
function showAlertBadge(stocks) {
    // 기존 배지 제거
    const existingBadge = document.querySelector('.alert-badge');
    if (existingBadge) {
        existingBadge.remove();
    }
    
    // 새 배지 생성
    const badge = document.createElement('div');
    badge.className = 'alert-badge';
    badge.innerHTML = `
        <span class="alert-icon">🔔</span>
        <span>${stocks.length}개 고확률 종목 발견!</span>
    `;
    badge.onclick = () => {
        showHighProbabilityStocksModal(stocks);
        badge.remove();
    };
    
    document.body.appendChild(badge);
    
    // 10초 후 자동 제거
    setTimeout(() => {
        if (badge.parentNode) {
            badge.remove();
        }
    }, 10000);
}

/**
 * 고확률 종목 모달 표시
 */
function showHighProbabilityStocksModal(stocks) {
    const stockList = stocks.map(stock => 
        `<div style="margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 8px;">
            <strong>${stock.stockName}</strong><br>
            <span style="color: #4caf50; font-weight: 600;">상승 확률: ${stock.upwardProbability.toFixed(1)}%</span>
        </div>`
    ).join('');
    
    const modalHtml = `
        <div style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; 
                    background: rgba(0,0,0,0.5); z-index: 3000; display: flex; 
                    align-items: center; justify-content: center;"
             onclick="this.remove()">
            <div style="background: white; padding: 30px; border-radius: 15px; 
                        max-width: 500px; width: 90%; max-height: 70vh; overflow-y: auto;"
                 onclick="event.stopPropagation()">
                <h2 style="margin-bottom: 20px;">🔔 고확률 상승 종목</h2>
                <p style="color: #666; margin-bottom: 20px;">
                    상승 확률 60% 이상 종목들입니다.
                </p>
                ${stockList}
                <button onclick="this.closest('div[onclick]').remove()"
                        style="margin-top: 20px; padding: 12px 24px; background: #667eea; 
                               color: white; border: none; border-radius: 8px; cursor: pointer; 
                               font-size: 14px; font-weight: 600;">
                    확인
                </button>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
}

function toggleInfo() {
  const header = document.querySelector('.header');
  const dashboard = document.querySelector('.market-dashboard');
  const modelInfo = document.querySelector('.model-info');

  if (header) header.style.display = (header.style.display === 'none' ? '' : 'none');
  if (dashboard) dashboard.style.display = (dashboard.style.display === 'none' ? '' : 'none');
  if (modelInfo) modelInfo.style.display = (modelInfo.style.display === 'none' ? '' : 'none');
}
