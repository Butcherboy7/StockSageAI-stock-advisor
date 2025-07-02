import requests
import os
from typing import Dict, List, Optional
import time
from datetime import datetime, timedelta
import re

# NLP libraries
try:
    import nltk
    from nltk.sentiment import SentimentIntensityAnalyzer
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    
    # Download required NLTK data
    nltk.download('vader_lexicon', quiet=True)
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except ImportError:
    print("NLTK not available")

try:
    import spacy
    # Load English model (will need to be downloaded: python -m spacy download en_core_web_sm)
    nlp = None
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        print("spaCy English model not found. Run: python -m spacy download en_core_web_sm")
except ImportError:
    print("spaCy not available")
    nlp = None

class SentimentAgent:
    """Agent responsible for sentiment analysis using NewsAPI + NLTK + spaCy"""
    
    def __init__(self):
        self.news_api_key = os.getenv("NEWS_API_KEY", "your_news_api_key")
        self.base_url = "https://newsapi.org/v2"
        self.cache = {}
        self.cache_duration = 3600  # 1 hour cache for news
        
        # Initialize sentiment analyzer
        try:
            self.sia = SentimentIntensityAnalyzer()
        except:
            self.sia = None
        
        # Headers for news API
        self.headers = {
            'X-API-Key': self.news_api_key,
            'User-Agent': 'Stock-Advisor-MVP/1.0'
        }
    
    def analyze_sentiment(self, ticker: str, company_name: str) -> Dict:
        """
        Analyze sentiment for a stock using news data
        
        Args:
            ticker: Stock ticker symbol
            company_name: Full company name
            
        Returns:
            Dictionary containing sentiment analysis results
        """
        try:
            # Check cache first
            cache_key = f"sentiment_{ticker}"
            if self._is_cached(cache_key):
                return self.cache[cache_key]['data']
            
            # Get news articles
            news_articles = self._get_news_articles(ticker, company_name)
            
            if not news_articles:
                return self._get_neutral_sentiment(ticker, "No news articles found")
            
            # Analyze sentiment
            sentiment_results = self._analyze_articles_sentiment(news_articles)
            
            # Combine with NER analysis if spaCy is available
            if nlp:
                ner_results = self._analyze_named_entities(news_articles)
                sentiment_results.update(ner_results)
            
            # Add metadata
            sentiment_results.update({
                'ticker': ticker,
                'company_name': company_name,
                'analysis_timestamp': time.time(),
                'total_articles': len(news_articles),
                'data_source': 'NewsAPI'
            })
            
            # Cache results
            self._cache_data(cache_key, sentiment_results)
            
            return sentiment_results
            
        except Exception as e:
            print(f"Error analyzing sentiment for {ticker}: {e}")
            return self._get_neutral_sentiment(ticker, f"Error: {str(e)}")
    
    def _get_news_articles(self, ticker: str, company_name: str) -> List[Dict]:
        """Fetch news articles from NewsAPI"""
        try:
            # Prepare search queries
            search_queries = [
                company_name,
                ticker,
                f"{company_name} stock",
                f"{ticker} share price"
            ]
            
            all_articles = []
            
            for query in search_queries[:2]:  # Limit to avoid API quota
                articles = self._search_news(query)
                all_articles.extend(articles)
                time.sleep(0.1)  # Small delay between requests
            
            # Remove duplicates based on title
            seen_titles = set()
            unique_articles = []
            
            for article in all_articles:
                title = article.get('title', '').lower()
                if title not in seen_titles and len(title) > 10:
                    seen_titles.add(title)
                    unique_articles.append(article)
            
            return unique_articles[:20]  # Limit to 20 most recent articles
            
        except Exception as e:
            print(f"Error fetching news for {ticker}: {e}")
            return []
    
    def _search_news(self, query: str) -> List[Dict]:
        """Search for news articles using NewsAPI"""
        try:
            # Calculate date range (last 7 days)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            params = {
                'q': query,
                'language': 'en',
                'sortBy': 'relevancy',
                'from': start_date.strftime('%Y-%m-%d'),
                'to': end_date.strftime('%Y-%m-%d'),
                'pageSize': 20
            }
            
            url = f"{self.base_url}/everything"
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('articles', [])
            else:
                print(f"NewsAPI error: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"Error searching news: {e}")
            return []
    
    def _analyze_articles_sentiment(self, articles: List[Dict]) -> Dict:
        """Analyze sentiment of news articles using NLTK VADER"""
        if not self.sia:
            return {
                'avg_sentiment': 0.0,
                'sentiment_distribution': {'positive': 0, 'neutral': 0, 'negative': 0},
                'error': 'NLTK VADER not available'
            }
        
        try:
            sentiments = []
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            
            detailed_analysis = []
            
            for article in articles:
                # Combine title and description for analysis
                text = ""
                if article.get('title'):
                    text += article['title'] + " "
                if article.get('description'):
                    text += article['description']
                
                if len(text.strip()) < 10:
                    continue
                
                # Get VADER sentiment scores
                scores = self.sia.polarity_scores(text)
                compound_score = scores['compound']
                sentiments.append(compound_score)
                
                # Classify sentiment
                if compound_score >= 0.05:
                    positive_count += 1
                    sentiment_label = 'positive'
                elif compound_score <= -0.05:
                    negative_count += 1
                    sentiment_label = 'negative'
                else:
                    neutral_count += 1
                    sentiment_label = 'neutral'
                
                detailed_analysis.append({
                    'title': article.get('title', '')[:100],
                    'sentiment_score': compound_score,
                    'sentiment_label': sentiment_label,
                    'published_at': article.get('publishedAt'),
                    'source': article.get('source', {}).get('name', 'Unknown')
                })
            
            # Calculate average sentiment
            avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0
            
            # Additional metrics
            total_articles = len(sentiments)
            sentiment_volatility = self._calculate_volatility(sentiments) if sentiments else 0.0
            
            return {
                'avg_sentiment': round(avg_sentiment, 3),
                'sentiment_range': [min(sentiments), max(sentiments)] if sentiments else [0, 0],
                'sentiment_volatility': round(sentiment_volatility, 3),
                'positive_count': positive_count,
                'negative_count': negative_count,
                'neutral_count': neutral_count,
                'sentiment_distribution': {
                    'positive': round(positive_count / total_articles * 100, 1) if total_articles > 0 else 0,
                    'negative': round(negative_count / total_articles * 100, 1) if total_articles > 0 else 0,
                    'neutral': round(neutral_count / total_articles * 100, 1) if total_articles > 0 else 0
                },
                'detailed_analysis': detailed_analysis[:10],  # Top 10 for display
                'analysis_method': 'NLTK VADER'
            }
            
        except Exception as e:
            print(f"Error in sentiment analysis: {e}")
            return self._get_neutral_sentiment("", f"Analysis error: {str(e)}")
    
    def _analyze_named_entities(self, articles: List[Dict]) -> Dict:
        """Analyze named entities using spaCy"""
        if not nlp:
            return {'ner_analysis': 'spaCy not available'}
        
        try:
            all_entities = []
            entity_sentiment = {}
            
            for article in articles:
                text = ""
                if article.get('title'):
                    text += article['title'] + " "
                if article.get('description'):
                    text += article['description']
                
                if len(text.strip()) < 10:
                    continue
                
                # Process with spaCy
                doc = nlp(text)
                
                # Extract entities
                for ent in doc.ents:
                    if ent.label_ in ['PERSON', 'ORG', 'PRODUCT', 'EVENT']:
                        entity_text = ent.text.lower()
                        all_entities.append({
                            'text': ent.text,
                            'label': ent.label_,
                            'article_title': article.get('title', '')[:50]
                        })
            
            # Count entity mentions
            entity_counts = {}
            for entity in all_entities:
                key = (entity['text'], entity['label'])
                entity_counts[key] = entity_counts.get(key, 0) + 1
            
            # Get top entities
            top_entities = sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                'top_entities': [
                    {'entity': entity[0], 'label': entity[1], 'mentions': count}
                    for (entity, label), count in top_entities
                ],
                'total_entities_found': len(all_entities),
                'unique_entities': len(entity_counts),
                'ner_model': 'spaCy en_core_web_sm'
            }
            
        except Exception as e:
            print(f"Error in NER analysis: {e}")
            return {'ner_analysis': f'Error: {str(e)}'}
    
    def _calculate_volatility(self, sentiments: List[float]) -> float:
        """Calculate sentiment volatility (standard deviation)"""
        if len(sentiments) < 2:
            return 0.0
        
        mean = sum(sentiments) / len(sentiments)
        variance = sum((x - mean) ** 2 for x in sentiments) / len(sentiments)
        return variance ** 0.5
    
    def _get_neutral_sentiment(self, ticker: str, reason: str) -> Dict:
        """Return neutral sentiment when analysis fails"""
        return {
            'ticker': ticker,
            'avg_sentiment': 0.0,
            'sentiment_range': [0.0, 0.0],
            'sentiment_volatility': 0.0,
            'positive_count': 0,
            'negative_count': 0,
            'neutral_count': 0,
            'sentiment_distribution': {'positive': 0, 'negative': 0, 'neutral': 100},
            'total_articles': 0,
            'analysis_timestamp': time.time(),
            'note': reason,
            'analysis_method': 'fallback'
        }
    
    def _is_cached(self, cache_key: str) -> bool:
        """Check if data is cached and still valid"""
        if cache_key not in self.cache:
            return False
        
        cache_time = self.cache[cache_key]['timestamp']
        return (time.time() - cache_time) < self.cache_duration
    
    def _cache_data(self, cache_key: str, data: Dict):
        """Cache data with timestamp"""
        self.cache[cache_key] = {
            'data': data,
            'timestamp': time.time()
        }
    
    def get_sentiment_summary(self, ticker: str) -> str:
        """Get a human-readable sentiment summary"""
        try:
            sentiment_data = self.analyze_sentiment(ticker, ticker)
            avg_sentiment = sentiment_data.get('avg_sentiment', 0.0)
            
            if avg_sentiment >= 0.1:
                return "Positive market sentiment"
            elif avg_sentiment <= -0.1:
                return "Negative market sentiment"
            else:
                return "Neutral market sentiment"
                
        except:
            return "Sentiment analysis unavailable"
