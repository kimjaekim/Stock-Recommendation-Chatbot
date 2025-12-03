/**
 * 포트폴리오 & 백테스팅 기능
 */

/**
 * 포트폴리오 표시
 */
async function showPortfolio() {
    try {
        console.log('포트폴리오 조회 시작');
        
        const response = await fetch('/api/portfolio');
        const data = await response.json();
        
        console.log('포트폴리오 데이터:', data);
        
        // 모달 생성
        const modal = document.createElement('div');
        modal.className = 'portfolio-modal';
        modal.onclick = (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
            }
        };
        
        const content = document.createElement('div');
        content.className = 'portfolio-content';
        
        // 헤더
        const header = document.createElement('div');
        header.className = 'portfolio-header';
        header.innerHTML = `
            <h2>💼 내 포트폴리오</h2>
            <button class="portfolio-close">✕ 닫기</button>
        `;
        header.querySelector('.portfolio-close').onclick = () => {
            document.body.removeChild(modal);
        };
        content.appendChild(header);
        
        const portfolio = data.portfolio;
        
        // 요약 정보
        const summary = document.createElement('div');
        summary.className = 'portfolio-summary';
        
        const totalInvestment = portfolio.totalInvestment || 0;
        const totalValue = portfolio.totalValue || 0;
        const totalProfit = portfolio.totalProfit || 0;
        const returnRate = portfolio.totalReturnRate || 0;
        
        summary.innerHTML = `
            <div class="summary-card">
                <div class="summary-label">총 투자금</div>
                <div class="summary-value">${totalInvestment.toLocaleString()}원</div>
            </div>
            <div class="summary-card">
                <div class="summary-label">평가액</div>
                <div class="summary-value">${totalValue.toLocaleString()}원</div>
            </div>
            <div class="summary-card">
                <div class="summary-label">수익률</div>
                <div class="summary-value" style="color: ${returnRate >= 0 ? '#4caf50' : '#f44336'}">
                    ${returnRate >= 0 ? '+' : ''}${returnRate.toFixed(2)}%
                </div>
            </div>
        `;
        content.appendChild(summary);
        
        // 종목 리스트
        if (portfolio.stocks && portfolio.stocks.length > 0) {
            portfolio.stocks.forEach(stock => {
                const stockDiv = document.createElement('div');
                stockDiv.className = 'portfolio-stock';
                
                const profit = stock.profit || 0;
                const returnRate = stock.returnRate || 0;
                const prediction = data.predictions[stock.ticker];
                
                stockDiv.innerHTML = `
                    <div class="stock-info">
                        <h3>${stock.stockName} (${stock.ticker})</h3>
                        <div class="stock-profit ${profit >= 0 ? 'positive' : 'negative'}">
                            ${profit >= 0 ? '+' : ''}${profit.toLocaleString()}원 (${returnRate.toFixed(2)}%)
                        </div>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 14px;">
                        <span>보유: ${stock.shares}주 × ${stock.purchasePrice.toLocaleString()}원</span>
                        <span>현재: ${stock.currentPrice.toLocaleString()}원</span>
                    </div>
                    ${prediction ? `
                        <div style="margin-top: 10px; padding: 10px; background: rgba(102, 126, 234, 0.1); border-radius: 8px;">
                            <strong>📊 AI 조언:</strong><br>
                            <span style="font-size: 13px;">
                                ${getPredictionAdvice(prediction)}
                            </span>
                        </div>
                    ` : ''}
                    <button onclick="removeFromPortfolio('${stock.ticker}')" 
                            style="margin-top: 10px; padding: 5px 15px; background: #f44336; color: white; border: none; border-radius: 5px; cursor: pointer;">
                        매도 기록
                    </button>
                `;
                content.appendChild(stockDiv);
            });
        } else {
            const emptyMsg = document.createElement('div');
            emptyMsg.style.textAlign = 'center';
            emptyMsg.style.padding = '40px';
            emptyMsg.style.color = '#999';
            emptyMsg.innerHTML = `
                <h3>📭 포트폴리오가 비어있습니다</h3>
                <p>추천 종목 카드에서 [포트폴리오에 추가] 버튼을 클릭하세요!</p>
            `;
            content.appendChild(emptyMsg);
        }
        
        modal.appendChild(content);
        document.body.appendChild(modal);
        
    } catch (error) {
        console.error('포트폴리오 조회 실패:', error);
        alert('포트폴리오 조회에 실패했습니다.');
    }
}

/**
 * 예측 기반 조언 생성
 */
function getPredictionAdvice(prediction) {
    const direction = prediction.direction.prediction;
    const risk = prediction.risk.prediction;
    const volatility = prediction.volatility.prediction;
    const upwardProb = direction === 1 
        ? prediction.direction.probability 
        : (1 - prediction.direction.probability);
    
    if (direction === 1 && risk === 0 && volatility === 0) {
        return `상승 예측 + 안전 + 저변동 → 보유 추천! (상승 확률 ${(upwardProb*100).toFixed(1)}%)`;
    } else if (direction === 0 && upwardProb < 0.5) {
        return `하락 예측 (${(100-upwardProb*100).toFixed(1)}%) → 손절 고려를 권장합니다.`;
    } else if (risk === 1) {
        return `⚠️ 손실 위험 높음 (${(prediction.risk.probability*100).toFixed(0)}%) → 신중한 결정이 필요합니다.`;
    } else {
        return `현재 상태 유지 관찰. 상승 확률 ${(upwardProb*100).toFixed(1)}%`;
    }
}

/**
 * 포트폴리오에서 제거
 */
async function removeFromPortfolio(ticker) {
    if (!confirm('이 종목을 포트폴리오에서 제거하시겠습니까?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/portfolio/remove/${ticker}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            alert('포트폴리오에서 제거되었습니다.');
            // 모달 닫고 다시 열기
            document.querySelector('.portfolio-modal')?.remove();
            showPortfolio();
        } else {
            throw new Error('제거 실패');
        }
    } catch (error) {
        console.error('제거 실패:', error);
        alert('제거에 실패했습니다.');
    }
}

/**
 * 오늘의 예측 검증 (실시간)
 */
async function showTodayVerification() {
    try {
        console.log('오늘의 예측 검증 시작');
        
        const response = await fetch('/api/verification/today');
        const data = await response.json();
        
        console.log('검증 데이터:', data);
        
        // 에러 처리
        if (data.error) {
            alert(`검증 실패: ${data.error}`);
            return;
        }
        
        // 모달 생성
        const modal = document.createElement('div');
        modal.className = 'backtest-modal';
        modal.onclick = (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
            }
        };
        
        const content = document.createElement('div');
        content.className = 'backtest-content';
        
        // 헤더
        const header = document.createElement('div');
        header.className = 'portfolio-header';
        header.innerHTML = `
            <h2>📊 오늘의 예측 검증 (실시간)</h2>
            <button class="portfolio-close">✕ 닫기</button>
        `;
        header.querySelector('.portfolio-close').onclick = () => {
            document.body.removeChild(modal);
        };
        content.appendChild(header);
        
        // 헤더 설명
        const description = document.createElement('div');
        description.style.cssText = `
            text-align: center;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            margin-bottom: 20px;
        `;
        
        const predictionDate = data.prediction_date || '알 수 없음';
        const targetDate = data.target_date || '알 수 없음';
        const verificationDate = data.verification_date || new Date().toISOString().split('T')[0];
        
        description.innerHTML = `
            <div style="font-size: 16px; font-weight: bold; margin-bottom: 10px;">
                📅 <strong>${predictionDate}</strong>에 예측한 결과를 검증합니다
            </div>
            <div style="font-size: 13px; opacity: 0.9; margin-bottom: 8px;">
                예측 생성: ${predictionDate} → 예측 대상: ${targetDate}
            </div>
            <div style="font-size: 12px; opacity: 0.8;">
                실시간 검증: ${new Date(data.timestamp).toLocaleString('ko-KR')}
            </div>
        `;
        content.appendChild(description);
        
        // 메인 성과 디스플레이
        const mainPerformance = document.createElement('div');
        mainPerformance.style.cssText = `
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        `;
        
        const accuracyCard = `
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        color: white; padding: 25px; border-radius: 15px; text-align: center;">
                <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">예측 정확도</div>
                <div style="font-size: 48px; font-weight: 800;">${data.accuracy.toFixed(1)}%</div>
                <div style="font-size: 12px; opacity: 0.8; margin-top: 5px;">
                    ${data.recommendations.filter(r => r.is_correct === true).length}/${data.recommendations.filter(r => r.is_correct !== null).length} 성공
                </div>
            </div>
        `;
        
        const returnCard = `
            <div style="background: linear-gradient(135deg, ${data.avg_return >= 0 ? '#4caf50, #45a049' : '#f44336, #e53935'}); 
                        color: white; padding: 25px; border-radius: 15px; text-align: center;">
                <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">평균 수익률</div>
                <div style="font-size: 48px; font-weight: 800;">
                    ${data.avg_return >= 0 ? '+' : ''}${data.avg_return.toFixed(2)}%
                </div>
                <div style="font-size: 12px; opacity: 0.8; margin-top: 5px;">
                    총 ${data.total_return >= 0 ? '+' : ''}${data.total_return.toFixed(2)}%
                </div>
            </div>
        `;
        
        mainPerformance.innerHTML = accuracyCard + returnCard;
        content.appendChild(mainPerformance);
        
        // 추천 종목 리스트
        if (data.recommendations && data.recommendations.length > 0) {
            const recommendationsSection = document.createElement('div');
            recommendationsSection.className = 'backtest-section';
            recommendationsSection.innerHTML = `
                <h3>🎯 오늘의 추천 Top 3</h3>
                <div class="stock-list">
                    ${data.recommendations.map((stock, index) => {
                        const isSuccess = stock.is_correct === true;
                        const isPending = stock.is_correct === null;
                        const returnClass = stock.actual_change > 0 ? 'positive' : 'negative';
                        
                        return `
                            <div class="stock-item" style="
                                background: ${isSuccess ? 'rgba(76, 175, 80, 0.1)' : (isPending ? 'rgba(255, 152, 0, 0.1)' : 'rgba(244, 67, 54, 0.1)')};
                                border: 2px solid ${isSuccess ? '#4caf50' : (isPending ? '#ff9800' : '#f44336')};
                                border-radius: 10px;
                                padding: 15px;
                                margin-bottom: 10px;
                            ">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <div>
                                        <div style="font-size: 18px; font-weight: bold; color: #333; margin-bottom: 5px;">
                                            ${index + 1}위. ${stock.stockName}
                                        </div>
                                        <div style="font-size: 13px; color: #666; margin-bottom: 8px;">
                                            예측: <strong>${stock.predicted_direction}</strong> (확률 ${stock.predicted_prob.toFixed(1)}%)
                                        </div>
                                        <div style="font-size: 12px; color: #999;">
                                            ${stock.start_price.toLocaleString()}원 → ${stock.current_price.toLocaleString()}원
                                        </div>
                                    </div>
                                    <div style="text-align: right;">
                                        <div style="font-size: 14px; font-weight: bold; margin-bottom: 5px; color: ${isSuccess ? '#4caf50' : (isPending ? '#ff9800' : '#f44336')};">
                                            ${stock.status}
                                        </div>
                                        <div class="stock-return ${returnClass}" style="font-size: 28px; font-weight: 800;">
                                            ${stock.actual_change >= 0 ? '+' : ''}${stock.actual_change.toFixed(2)}%
                                        </div>
                                        <div style="font-size: 11px; color: #999; margin-top: 3px;">
                                            ${stock.actual_direction}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
            `;
            content.appendChild(recommendationsSection);
        } else {
            const noDataSection = document.createElement('div');
            noDataSection.style.cssText = `
                text-align: center;
                padding: 40px;
                color: #999;
            `;
            noDataSection.innerHTML = `
                <h3>📭 추천 데이터가 없습니다</h3>
                <p>예측 데이터를 먼저 생성해주세요.</p>
            `;
            content.appendChild(noDataSection);
        }
        
        // 투자 시뮬레이션
        if (data.recommendations && data.recommendations.length > 0 && data.avg_return !== 0) {
            const simulationSection = document.createElement('div');
            simulationSection.style.cssText = `
                margin-top: 20px; 
                padding: 20px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; 
                border-radius: 15px; 
                text-align: center;
            `;
            
            const initialInvestment = 1000000; // 100만원 기준
            const perStock = initialInvestment / 3; // 3개 종목에 균등 분배
            const finalValue = initialInvestment + (initialInvestment * (data.total_return / 100));
            const profit = finalValue - initialInvestment;
            
            simulationSection.innerHTML = `
                <div style="font-size: 16px; opacity: 0.9; margin-bottom: 15px;">
                    💰 <strong>투자 시뮬레이션</strong> (100만원 기준)
                </div>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 15px;">
                    <div>
                        <div style="font-size: 12px; opacity: 0.8;">초기 투자</div>
                        <div style="font-size: 20px; font-weight: 800;">${initialInvestment.toLocaleString()}원</div>
                    </div>
                    <div>
                        <div style="font-size: 12px; opacity: 0.8;">종목당 투자</div>
                        <div style="font-size: 20px; font-weight: 800;">${perStock.toLocaleString()}원</div>
                    </div>
                    <div>
                        <div style="font-size: 12px; opacity: 0.8;">최종 평가액</div>
                        <div style="font-size: 20px; font-weight: 800;">${finalValue.toLocaleString()}원</div>
                    </div>
                </div>
                <div style="font-size: 32px; font-weight: 800; margin-top: 15px;">
                    ${profit >= 0 ? '💰 수익' : '📉 손실'}: ${profit >= 0 ? '+' : ''}${profit.toLocaleString()}원
                </div>
            `;
            content.appendChild(simulationSection);
        }
        
        modal.appendChild(content);
        document.body.appendChild(modal);
        
    } catch (error) {
        console.error('검증 조회 실패:', error);
        alert('검증 결과 조회에 실패했습니다.');
    }
}

