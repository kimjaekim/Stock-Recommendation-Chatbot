"""
챗봇 응답 로직
- today_predictions.json을 읽어서 안전한 종목 추천
- 키워드 파악 및 금액 배분
"""

import json
import re
from datetime import datetime
from stock_name_mapping import get_stock_name

class ChatResponseSystem:
    def __init__(self):
        self.predictions = {}
        self.current_prices = {}
        
    def load_today_predictions(self):
        """오늘의 예측 결과 로드"""
        try:
            with open('today_predictions.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.predictions = data['predictions']
            print(f"✅ 오늘의 예측 로드 완료: {data['date']}")
            return True
        except Exception as e:
            print(f"❌ 예측 데이터 로드 실패: {e}")
            return False
    
    def parse_user_request(self, user_message):
        """사용자 요청 파싱"""
        # 금액 추출
        amount_match = re.search(r'(\d+)\s*만원|(\d+)\s*원|(\d+)만|(\d+)원', user_message)
        amount = 0
        if amount_match:
            for group in amount_match.groups():
                if group:
                    num = int(group)
                    if '만' in user_message or '만원' in user_message:
                        amount = num * 10000
                    else:
                        amount = num
                    break
        
        # 안전성 키워드
        safety_keywords = ['안전', '안정', '보수', '위험 없', '리스크 없']
        is_safe = any(keyword in user_message for keyword in safety_keywords)
        
        # 공격성 키워드
        aggressive_keywords = ['공격', '수익', '높은', '최대']
        is_aggressive = any(keyword in user_message for keyword in aggressive_keywords)
        
        return {
            'amount': amount,
            'is_safe': is_safe,
            'is_aggressive': is_aggressive
        }
    
    def filter_stocks(self, user_request):
        """종목 필터링"""
        filtered = []
        
        for ticker, pred in self.predictions.items():
            risk = pred.get('risk', {}).get('prediction', 1)
            volatility = pred.get('volatility', {}).get('prediction', 1)
            direction = pred.get('direction', {}).get('prediction', 0)
            
            # 안전 필터
            if user_request['is_safe']:
                if risk == 0 and volatility == 0:
                    filtered.append({
                        'ticker': ticker,
                        'prediction': pred,
                        'priority': direction  # 상승이면 우선순위 높음
                    })
            # 공격 필터
            elif user_request['is_aggressive']:
                if direction == 1:  # 상승 예상
                    filtered.append({
                        'ticker': ticker,
                        'prediction': pred,
                        'priority': pred.get('score', 0)
                    })
            # 기본 (안전 + 상승)
            else:
                if risk == 0 and volatility == 0 and direction == 1:
                    filtered.append({
                        'ticker': ticker,
                        'prediction': pred,
                        'priority': pred.get('score', 0)
                    })
        
        # 우선순위 정렬
        filtered.sort(key=lambda x: x['priority'], reverse=True)
        
        return filtered
    
    def allocate_amount(self, stocks, amount):
        """금액 배분"""
        if amount == 0 or len(stocks) == 0:
            return []
        
        # 상위 5개만 선택
        selected = stocks[:5]
        
        # 동일 비중 배분
        per_stock = amount / len(selected)
        
        allocations = []
        for stock in selected:
            ticker = stock['ticker']
            price = stock['prediction'].get('currentPrice', 0)
            
            if price > 0:
                shares = int(per_stock / price)
                allocated_amount = shares * price
                
                allocations.append({
                    'ticker': ticker,
                    'name': get_stock_name(ticker),
                    'shares': shares,
                    'amount': allocated_amount,
                    'price': price,
                    'prediction': stock['prediction']
                })
        
        return allocations
    
    def generate_response(self, allocations, user_request):
        """응답 생성"""
        if not allocations:
            return "❌ 추천할 종목을 찾을 수 없습니다. 조건을 변경해보세요."
        
        response = f"💰 투자 금액: {user_request['amount']:,}원\n\n"
        response += "📊 추천 종목:\n\n"
        
        total_amount = 0
        for i, alloc in enumerate(allocations, 1):
            rec = alloc['prediction'].get('recommendation', '보유')
            direction_prob = alloc['prediction'].get('direction', {}).get('probability', 0)
            
            response += f"{i}. **{alloc['name']}** ({alloc['ticker']})\n"
            response += f"   - 추천: {rec}\n"
            response += f"   - 매수: {alloc['shares']}주 ({alloc['amount']:,}원)\n"
            response += f"   - 현재가: {alloc['price']:,}원\n"
            response += f"   - 상승 확률: {direction_prob:.1%}\n\n"
            
            total_amount += alloc['amount']
        
        response += f"💵 총 투자액: {total_amount:,}원\n"
        
        return response
    
    def process_message(self, user_message):
        """메시지 처리"""
        # 예측 데이터 로드
        if not self.load_today_predictions():
            return "❌ 예측 데이터를 불러올 수 없습니다."
        
        # 요청 파싱
        user_request = self.parse_user_request(user_message)
        
        if user_request['amount'] == 0:
            return "💰 투자 금액을 알려주세요. 예: '100만원으로 안전하게 추천해줘'"
        
        # 종목 필터링
        filtered_stocks = self.filter_stocks(user_request)
        
        if not filtered_stocks:
            return "❌ 조건에 맞는 종목을 찾을 수 없습니다."
        
        # 금액 배분
        allocations = self.allocate_amount(filtered_stocks, user_request['amount'])
        
        # 응답 생성
        response = self.generate_response(allocations, user_request)
        
        return response

def main():
    """테스트"""
    system = ChatResponseSystem()
    
    test_messages = [
        "100만원으로 안전하게 추천해줘",
        "50만원으로 공격적으로 투자하고 싶어",
        "200만원으로 추천해줘"
    ]
    
    for msg in test_messages:
        print(f"\n{'='*60}")
        print(f"사용자: {msg}")
        print(f"{'='*60}")
        response = system.process_message(msg)
        print(response)

if __name__ == "__main__":
    main()

