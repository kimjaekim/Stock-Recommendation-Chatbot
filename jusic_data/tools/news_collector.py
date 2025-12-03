"""
네이버 뉴스 수집 및 감정분석
- 종목별 최근 뉴스 수집
- 감정 점수 계산
- 캐싱 시스템
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import pickle
import os
from datetime import datetime, timedelta
import time
import sys
from pathlib import Path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))
from utils.sentiment_keywords import calculate_sentiment_score, classify_sentiment
from utils.stock_name_mapping import STOCK_NAME_MAPPING

class NewsCollector:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.cache_file = 'cached_data/news_sentiment_cache.pkl'
        
    def get_stock_name(self, ticker):
        """티커에서 종목명 추출"""
        return STOCK_NAME_MAPPING.get(ticker, ticker)
    
    def search_naver_news(self, stock_name, days=7, max_news=20):
        """
        네이버 뉴스 검색
        
        Args:
            stock_name: 종목명 (예: '삼성전자')
            days: 최근 며칠 (기본 7일)
            max_news: 최대 뉴스 수
        
        Returns:
            list: [{'title': str, 'date': str, 'link': str}, ...]
        """
        news_list = []
        
        try:
            # 네이버 뉴스 검색 URL
            query = f"{stock_name} 주식"
            url = f"https://search.naver.com/search.naver?where=news&query={query}&sort=1"  # sort=1: 최신순
            
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                print(f"    WARNING: Failed to fetch news for {stock_name} (status {response.status_code})")
                return news_list
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 뉴스 아이템 파싱
            news_items = soup.select('.news_area')
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            for item in news_items[:max_news]:
                try:
                    # 제목
                    title_elem = item.select_one('.news_tit')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    link = title_elem.get('href', '')
                    
                    # 날짜는 간단히 현재로 설정 (상세 파싱 복잡)
                    news_list.append({
                        'title': title,
                        'link': link,
                        'date': datetime.now().strftime('%Y-%m-%d')
                    })
                    
                except Exception as e:
                    continue
            
            time.sleep(0.5)  # API 호출 제한 방지
            
        except Exception as e:
            print(f"    ERROR: {stock_name} news search failed: {e}")
        
        return news_list
    
    def calculate_sentiment_for_stock(self, ticker, news_list):
        """
        종목별 감정 점수 계산
        
        Args:
            ticker: 종목 티커
            news_list: 뉴스 리스트
        
        Returns:
            dict: 감정 분석 결과
        """
        if not news_list:
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
        
        for news in news_list:
            title = news['title']
            score = calculate_sentiment_score(title)
            sentiment_class = classify_sentiment(score)
            
            sentiments.append(score)
            
            if sentiment_class == 'positive':
                positive_count += 1
            elif sentiment_class == 'negative':
                negative_count += 1
            else:
                neutral_count += 1
        
        # 평균 감정 점수
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0
        
        return {
            'ticker': ticker,
            'news_count': len(news_list),
            'sentiment_score': avg_sentiment,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'sentiment_class': classify_sentiment(avg_sentiment),
            'positive_ratio': positive_count / len(news_list) if news_list else 0,
            'negative_ratio': negative_count / len(news_list) if news_list else 0
        }
    
    def collect_sentiment_for_tickers(self, tickers, days=7, max_news=20):
        """
        여러 종목의 감정 데이터 수집
        
        Args:
            tickers: 티커 리스트
            days: 최근 며칠
            max_news: 종목당 최대 뉴스 수
        
        Returns:
            dict: {ticker: sentiment_data}
        """
        print("="*80)
        print("News Sentiment Collection")
        print("="*80)
        print(f"\nCollecting news for {len(tickers)} stocks...")
        print(f"Period: Last {days} days")
        print(f"Max news per stock: {max_news}")
        print()
        
        sentiment_data = {}
        
        for idx, ticker in enumerate(tickers, 1):
            stock_name = self.get_stock_name(ticker)
            print(f"[{idx}/{len(tickers)}] {ticker} ({stock_name})...")
            
            # 뉴스 수집
            news_list = self.search_naver_news(stock_name, days, max_news)
            
            # 감정 분석
            sentiment = self.calculate_sentiment_for_stock(ticker, news_list)
            sentiment_data[ticker] = sentiment
            
            print(f"    News: {sentiment['news_count']}, "
                  f"Sentiment: {sentiment['sentiment_score']:+.2f} ({sentiment['sentiment_class']}), "
                  f"Pos: {sentiment['positive_count']}, Neg: {sentiment['negative_count']}")
        
        return sentiment_data
    
    def save_cache(self, sentiment_data):
        """캐시 저장"""
        os.makedirs('cached_data', exist_ok=True)
        
        cache = {
            'data': sentiment_data,
            'collection_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'stocks': list(sentiment_data.keys())
        }
        
        with open(self.cache_file, 'wb') as f:
            pickle.dump(cache, f)
        
        print(f"\nCache saved: {self.cache_file}")
    
    def load_cache(self, max_age_hours=6):
        """
        캐시 로드
        
        Args:
            max_age_hours: 최대 캐시 유효 시간 (시간)
        
        Returns:
            dict or None
        """
        if not os.path.exists(self.cache_file):
            return None
        
        cache_time = datetime.fromtimestamp(os.path.getmtime(self.cache_file))
        age_hours = (datetime.now() - cache_time).total_seconds() / 3600
        
        if age_hours > max_age_hours:
            print(f"[Cache] Cache too old ({age_hours:.1f}h), re-collecting...")
            return None
        
        print(f"[Cache] Loading cached sentiment data ({age_hours:.1f}h old)...")
        with open(self.cache_file, 'rb') as f:
            cache = pickle.load(f)
        
        print(f"  Stocks: {len(cache['data'])}")
        print(f"  Collection date: {cache['collection_date']}")
        
        return cache['data']

def merge_sentiment_features(stock_df, sentiment_data, ticker):
    """
    주가 데이터에 감정 특징 추가
    
    Args:
        stock_df: 주가 데이터
        sentiment_data: 감정 데이터 dict
        ticker: 티커
    
    Returns:
        DataFrame: 감정 특징이 추가된 데이터
    """
    df = stock_df.copy()
    
    if ticker not in sentiment_data:
        return df
    
    sentiment = sentiment_data[ticker]
    
    # 감정 특징 추가 (최근 데이터에만 적용)
    # 전체 기간에 동일한 값 적용 (간단한 방법)
    df['Sentiment_Score'] = sentiment['sentiment_score']
    df['Positive_Ratio'] = sentiment['positive_ratio']
    df['Negative_Ratio'] = sentiment['negative_ratio']
    df['News_Volume'] = sentiment['news_count']
    
    return df

# 테스트
if __name__ == '__main__':
    collector = NewsCollector()
    
    # 테스트: 5개 종목
    test_tickers = ['005930.KS', '000660.KS', '035420.KS', '035720.KS', '005380.KS']
    
    sentiment_data = collector.collect_sentiment_for_tickers(test_tickers, days=7, max_news=10)
    
    # 캐시 저장
    collector.save_cache(sentiment_data)
    
    print("\n" + "="*80)
    print("Collection Complete!")
    print("="*80)

