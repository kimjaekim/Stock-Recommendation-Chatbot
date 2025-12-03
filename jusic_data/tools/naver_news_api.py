"""
네이버 뉴스 검색 API 활용
- 공식 API로 안정적인 뉴스 수집
- 감정분석 적용
"""

import requests
import urllib.parse
import pickle
import os
from datetime import datetime
import time
from sentiment_keywords import calculate_sentiment_score, classify_sentiment
import sys
from pathlib import Path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))
from utils.stock_name_mapping import STOCK_NAME_MAPPING

class NaverNewsAPI:
    def __init__(self, client_id=None, client_secret=None):
        """
        Args:
            client_id: 네이버 API 클라이언트 ID
            client_secret: 네이버 API 클라이언트 시크릿
        """
        # API 키 설정 (환경변수 또는 파일에서 로드)
        self.client_id = client_id or os.getenv('NAVER_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('NAVER_CLIENT_SECRET')
        
        # API 키 파일에서 로드 시도
        if not self.client_id:
            self.load_api_keys()
        
        self.base_url = "https://openapi.naver.com/v1/search/news.json"
        self.cache_file = 'cached_data/naver_api_news_cache.pkl'
    
    def load_api_keys(self):
        """API 키 파일에서 로드"""
        key_file = 'naver_api_keys.txt'
        
        if os.path.exists(key_file):
            with open(key_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if len(lines) >= 2:
                    self.client_id = lines[0].strip()
                    self.client_secret = lines[1].strip()
                    print("[API Keys] Loaded from file")
        else:
            print(f"[API Keys] Please create '{key_file}' with:")
            print("  Line 1: YOUR_CLIENT_ID")
            print("  Line 2: YOUR_CLIENT_SECRET")
            print("\nGet your keys from: https://developers.naver.com/apps/#/register")
    
    def search_news(self, query, display=20, sort='date'):
        """
        네이버 뉴스 검색
        
        Args:
            query: 검색어
            display: 검색 결과 개수 (최대 100)
            sort: 정렬 (date: 날짜순, sim: 정확도순)
        
        Returns:
            list: 뉴스 아이템 리스트
        """
        if not self.client_id or not self.client_secret:
            print("ERROR: API keys not configured")
            return []
        
        try:
            encoded_query = urllib.parse.quote(query)
            url = f"{self.base_url}?query={encoded_query}&display={display}&sort={sort}"
            
            headers = {
                'X-Naver-Client-Id': self.client_id,
                'X-Naver-Client-Secret': self.client_secret
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('items', [])
            else:
                print(f"  API Error: {response.status_code}")
                return []
        
        except Exception as e:
            print(f"  ERROR: {e}")
            return []
    
    def calculate_sentiment_for_stock(self, ticker, stock_name):
        """
        종목별 뉴스 수집 및 감정 분석
        
        Args:
            ticker: 종목 티커
            stock_name: 종목명
        
        Returns:
            dict: 감정 분석 결과
        """
        query = f"{stock_name} 주식"
        news_items = self.search_news(query, display=20, sort='date')
        
        if not news_items:
            return {
                'ticker': ticker,
                'news_count': 0,
                'sentiment_score': 0.0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'sentiment_class': 'neutral'
            }
        
        sentiments = []
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for item in news_items:
            # HTML 태그 제거
            title = item['title'].replace('<b>', '').replace('</b>', '').replace('&quot;', '"')
            
            score = calculate_sentiment_score(title)
            sentiment_class = classify_sentiment(score)
            
            sentiments.append(score)
            
            if sentiment_class == 'positive':
                positive_count += 1
            elif sentiment_class == 'negative':
                negative_count += 1
            else:
                neutral_count += 1
        
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0
        
        return {
            'ticker': ticker,
            'news_count': len(news_items),
            'sentiment_score': avg_sentiment,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'sentiment_class': classify_sentiment(avg_sentiment),
            'positive_ratio': positive_count / len(news_items) if news_items else 0,
            'negative_ratio': negative_count / len(news_items) if news_items else 0,
            'sample_titles': [item['title'].replace('<b>', '').replace('</b>', '') 
                             for item in news_items[:3]]
        }
    
    def collect_sentiment_for_tickers(self, tickers):
        """
        여러 종목의 뉴스 감정 수집
        
        Args:
            tickers: 티커 리스트
        
        Returns:
            dict: {ticker: sentiment_data}
        """
        print("="*80)
        print("Naver News API - Sentiment Collection")
        print("="*80)
        print(f"\nCollecting news for {len(tickers)} stocks...")
        print()
        
        sentiment_data = {}
        
        for idx, ticker in enumerate(tickers, 1):
            stock_name = STOCK_NAME_MAPPING.get(ticker, ticker)
            print(f"[{idx}/{len(tickers)}] {ticker} ({stock_name})...")
            
            result = self.calculate_sentiment_for_stock(ticker, stock_name)
            sentiment_data[ticker] = result
            
            print(f"    News: {result['news_count']}, "
                  f"Sentiment: {result['sentiment_score']:+.2f} ({result['sentiment_class']}), "
                  f"Pos/Neg/Neu: {result['positive_count']}/{result['negative_count']}/{result['neutral_count']}")
            
            if result.get('sample_titles'):
                print(f"    Sample: {result['sample_titles'][0][:60]}...")
            
            time.sleep(0.1)  # API 호출 제한 방지
        
        return sentiment_data
    
    def save_cache(self, sentiment_data):
        """캐시 저장"""
        os.makedirs('cached_data', exist_ok=True)
        
        cache = {
            'data': sentiment_data,
            'collection_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'stocks': list(sentiment_data.keys()),
            'source': 'Naver News API (Official)'
        }
        
        with open(self.cache_file, 'wb') as f:
            pickle.dump(cache, f)
        
        print(f"\nCache saved: {self.cache_file}")

# 테스트
if __name__ == '__main__':
    api = NaverNewsAPI()
    
    if not api.client_id:
        print("\n" + "="*80)
        print("API KEY SETUP REQUIRED")
        print("="*80)
        print("\n1. Go to: https://developers.naver.com/apps/#/register")
        print("2. Register application")
        print("3. Get Client ID and Client Secret")
        print("4. Create 'naver_api_keys.txt' in this directory:")
        print("   Line 1: YOUR_CLIENT_ID")
        print("   Line 2: YOUR_CLIENT_SECRET")
        print("\nExample naver_api_keys.txt:")
        print("  abc123xyz")
        print("  def456uvw")
    else:
        # 테스트: 3개 종목
        test_tickers = ['005930.KS', '000660.KS', '035420.KS']
        
        sentiment_data = api.collect_sentiment_for_tickers(test_tickers)
        
        # 캐시 저장
        api.save_cache(sentiment_data)
        
        print("\n" + "="*80)
        print("Test Complete!")
        print("="*80)

