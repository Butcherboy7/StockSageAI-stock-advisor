# Smart Stock Advisor MVP

## Overview

This is a multi-agent AI system designed for intelligent stock analysis, built as a hackathon MVP. The system combines fundamental analysis, sentiment analysis, and data aggregation to provide stock recommendations (BUY/HOLD/SELL) for Indian market stocks.

The application uses a Streamlit frontend with multiple specialized agents working together to analyze stocks from different perspectives and provide comprehensive investment advice.

## System Architecture

### Frontend
- **Streamlit Web Application**: Simple, interactive web interface for user interaction
- **Real-time Analysis**: Dynamic weight adjustment between fundamental and sentiment analysis
- **Caching Interface**: Visual feedback on data freshness and cache status

### Backend Architecture
- **Multi-Agent System**: Four specialized agents handling different aspects of analysis
- **Caching Layer**: Two-tier caching (memory + file-based) to reduce API calls
- **Data Normalization**: Standardized scoring system across all agents

### Agent Architecture
1. **Screening Agent**: Web scraping from screener.in with fallback to hardcoded stocks
2. **Fundamental Agent**: Financial data analysis using yfinance API
3. **Sentiment Agent**: News analysis using NewsAPI + NLTK + spaCy
4. **Aggregator Agent**: Score combination and recommendation generation

## Key Components

### Agents (`/agents/`)
- **ScreeningAgent**: Stock discovery and basic market data
  - Primary: Web scraping from screener.in
  - Fallback: Hardcoded Indian stock tickers (RELIANCE.NS, TCS.NS, etc.)
  
- **FundamentalAgent**: Financial metrics analysis
  - Uses yfinance for real-time data
  - Calculates PE ratio, PB ratio, ROE, debt-to-equity, profit margins
  - Handles Indian stock suffixes (.NS)
  
- **SentimentAgent**: News sentiment analysis
  - NewsAPI integration for latest headlines
  - NLTK VADER sentiment analyzer
  - spaCy NLP pipeline for entity recognition
  - Sentiment scoring on -1 to 1 scale
  
- **AggregatorAgent**: Final recommendation engine
  - Weighted combination of fundamental and sentiment scores
  - Configurable weights (default 50/50)
  - BUY/HOLD/SELL classification based on score thresholds

### Utilities (`/utils/`)
- **CacheManager**: Two-tier caching system
  - Memory cache for immediate access
  - File-based cache for persistence
  - Configurable TTL (default 1 hour)
  
- **DataNormalizer**: Score standardization
  - Indian market benchmarks for fundamental metrics
  - 0-100 scoring system
  - Handles missing data gracefully

### Main Application (`app.py`)
- Streamlit configuration and UI setup
- Agent initialization and orchestration
- User preference management

## Data Flow

1. **Stock Selection**: Screening agent provides list of stocks to analyze
2. **Parallel Analysis**: 
   - Fundamental agent fetches financial metrics via yfinance
   - Sentiment agent retrieves and analyzes news via NewsAPI
3. **Data Normalization**: Raw scores converted to 0-100 scale
4. **Aggregation**: Weighted combination of normalized scores
5. **Recommendation**: Final BUY/HOLD/SELL decision based on aggregated score
6. **Caching**: Results cached to minimize API calls and improve performance

## External Dependencies

### APIs
- **yfinance**: Stock fundamental data (no authentication required)
- **NewsAPI**: Latest news headlines (requires free API key)
- **screener.in**: Indian stock screening data (web scraping)

### NLP Libraries
- **NLTK**: VADER sentiment analyzer, tokenization, stopwords
- **spaCy**: Named entity recognition and advanced NLP (requires en_core_web_sm model)

### Core Libraries
- **Streamlit**: Web application framework
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computations
- **requests**: HTTP client for API calls
- **BeautifulSoup**: HTML parsing for web scraping

## Deployment Strategy

This is a hackathon MVP designed for local demonstration:

1. **Local Development**: Run via `streamlit run app.py`
2. **Environment Setup**: 
   - Install requirements: `pip install -r requirements.txt`
   - Download spaCy model: `python -m spacy download en_core_web_sm`
   - Set NEWS_API_KEY environment variable
3. **Demo Mode**: Includes fallback mechanisms for when external services are unavailable
4. **No Production Deployment**: System is optimized for demonstration, not production use

## Changelog

Changelog:
- July 02, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.