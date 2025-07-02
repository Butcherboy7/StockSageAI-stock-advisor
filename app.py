import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime
import os

# Import our custom agents
from agents.screening_agent import ScreeningAgent
from agents.fundamental_agent import FundamentalAgent
from agents.sentiment_agent import SentimentAgent
from agents.aggregator_agent import AggregatorAgent
from utils.cache_manager import CacheManager
from utils.data_normalizer import DataNormalizer

# Configure page
st.set_page_config(
    page_title="Smart Stock Advisor MVP",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize cache manager
@st.cache_resource
def get_cache_manager():
    return CacheManager()

# Initialize agents
@st.cache_resource
def initialize_agents():
    screening_agent = ScreeningAgent()
    fundamental_agent = FundamentalAgent()
    sentiment_agent = SentimentAgent()
    aggregator_agent = AggregatorAgent()
    data_normalizer = DataNormalizer()
    
    return screening_agent, fundamental_agent, sentiment_agent, aggregator_agent, data_normalizer

def main():
    st.title("🤖 Smart Stock Advisor MVP")
    st.markdown("### Multi-Agent AI System for Intelligent Stock Analysis")
    
    # Initialize components
    cache_manager = get_cache_manager()
    screening_agent, fundamental_agent, sentiment_agent, aggregator_agent, data_normalizer = initialize_agents()
    
    # Sidebar controls
    st.sidebar.header("⚙️ Analysis Configuration")
    
    # Weight adjustment sliders
    st.sidebar.subheader("Weight Distribution")
    fundamental_weight = st.sidebar.slider(
        "Fundamental Analysis Weight (%)",
        min_value=0,
        max_value=100,
        value=50,
        step=5,
        help="Weight given to fundamental metrics like PE, PB, ROE"
    )
    
    sentiment_weight = 100 - fundamental_weight
    st.sidebar.write(f"Sentiment Analysis Weight: {sentiment_weight}%")
    
    # Number of stocks to analyze
    num_stocks = st.sidebar.selectbox(
        "Number of stocks to analyze",
        options=[5, 10, 15, 20],
        index=1,
        help="More stocks = longer analysis time"
    )
    
    # Analysis trigger
    analyze_button = st.sidebar.button("🚀 Start Analysis", type="primary")
    
    # Main content area
    if analyze_button:
        with st.spinner("🔍 Multi-Agent Analysis in Progress..."):
            try:
                # Progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Step 1: Screening Agent
                status_text.text("🎯 Screening Agent: Finding top stocks...")
                progress_bar.progress(10)
                
                screening_results = screening_agent.get_top_stocks(num_stocks)
                if not screening_results:
                    st.error("❌ Failed to retrieve stock data from screening agent")
                    return
                
                st.success(f"✅ Found {len(screening_results)} stocks for analysis")
                progress_bar.progress(25)
                
                # Step 2: Fundamental Analysis Agent
                status_text.text("📊 Fundamental Agent: Analyzing financial metrics...")
                
                fundamental_data = {}
                for i, stock in enumerate(screening_results):
                    ticker = stock['ticker']
                    fundamental_data[ticker] = fundamental_agent.analyze_stock(ticker)
                    progress_bar.progress(25 + (i + 1) * 25 // len(screening_results))
                
                progress_bar.progress(50)
                
                # Step 3: Sentiment Analysis Agent
                status_text.text("📰 Sentiment Agent: Analyzing market sentiment...")
                
                sentiment_data = {}
                for i, stock in enumerate(screening_results):
                    ticker = stock['ticker']
                    company_name = stock['name']
                    sentiment_data[ticker] = sentiment_agent.analyze_sentiment(ticker, company_name)
                    progress_bar.progress(50 + (i + 1) * 25 // len(screening_results))
                
                progress_bar.progress(75)
                
                # Step 4: Aggregator Agent
                status_text.text("🔧 Aggregator Agent: Combining analysis results...")
                
                final_results = []
                for stock in screening_results:
                    ticker = stock['ticker']
                    
                    # Get normalized scores
                    fundamental_score = data_normalizer.normalize_fundamental_score(
                        fundamental_data.get(ticker, {})
                    )
                    sentiment_score = data_normalizer.normalize_sentiment_score(
                        sentiment_data.get(ticker, {})
                    )
                    
                    # Aggregate scores
                    aggregated_result = aggregator_agent.aggregate_scores(
                        ticker=ticker,
                        company_name=stock['name'],
                        screening_data=stock,
                        fundamental_data=fundamental_data.get(ticker, {}),
                        sentiment_data=sentiment_data.get(ticker, {}),
                        fundamental_weight=fundamental_weight / 100,
                        sentiment_weight=sentiment_weight / 100
                    )
                    
                    final_results.append(aggregated_result)
                
                progress_bar.progress(100)
                status_text.text("✨ Analysis Complete!")
                
                # Clear progress indicators
                time.sleep(1)
                progress_bar.empty()
                status_text.empty()
                
                # Display results
                display_results(final_results, fundamental_weight, sentiment_weight)
                
            except Exception as e:
                st.error(f"❌ Analysis failed: {str(e)}")
                st.exception(e)
    
    else:
        # Welcome screen
        st.markdown("""
        ## 🎯 How It Works
        
        Our multi-agent system analyzes Indian stocks through four specialized agents:
        
        **🔍 Screening Agent**
        - Scrapes real-time data from screener.in
        - Identifies top-performing stocks by market cap
        
        **📊 Fundamental Analysis Agent**
        - Uses yfinance for live financial metrics
        - Analyzes PE ratio, PB ratio, ROE, and more
        
        **📰 Sentiment Analysis Agent**
        - Fetches latest news via NewsAPI
        - Applies NLTK VADER + spaCy NLP analysis
        
        **🔧 Aggregator Agent**
        - Combines fundamental and sentiment scores
        - Provides BUY/HOLD/SELL recommendations
        
        ### 🚀 Get Started
        Adjust the analysis weights in the sidebar and click "Start Analysis" to begin!
        """)
        
        # Display sample configuration
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("""
            **📊 API Requirements**
            - NewsAPI key (from environment)
            - Internet connection for scraping
            - No other authentication needed
            """)
        
        with col2:
            st.warning("""
            **⚡ Performance Notes**
            - Analysis takes 30-60 seconds
            - Caching reduces repeated requests
            - Respects rate limits automatically
            """)

def display_results(results, fundamental_weight, sentiment_weight):
    """Display comprehensive analysis results"""
    
    st.markdown("## 📈 Analysis Results")
    
    # Sort by overall score
    results_sorted = sorted(results, key=lambda x: x['overall_score'], reverse=True)
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    buy_count = len([r for r in results_sorted if r['recommendation'] == 'BUY'])
    hold_count = len([r for r in results_sorted if r['recommendation'] == 'HOLD'])
    sell_count = len([r for r in results_sorted if r['recommendation'] == 'SELL'])
    avg_score = np.mean([r['overall_score'] for r in results_sorted])
    
    col1.metric("🟢 BUY Recommendations", buy_count)
    col2.metric("🟡 HOLD Recommendations", hold_count)
    col3.metric("🔴 SELL Recommendations", sell_count)
    col4.metric("📊 Average Score", f"{avg_score:.1f}/100")
    
    # Configuration display
    st.markdown(f"**Current Weights:** Fundamental: {fundamental_weight}% | Sentiment: {sentiment_weight}%")
    
    # Detailed results table
    st.markdown("### 📋 Detailed Analysis")
    
    # Prepare data for display
    display_data = []
    for result in results_sorted:
        display_data.append({
            'Rank': len(display_data) + 1,
            'Company': result['company_name'],
            'Ticker': result['ticker'],
            'Recommendation': result['recommendation'],
            'Overall Score': f"{result['overall_score']:.1f}/100",
            'Fundamental Score': f"{result['fundamental_score']:.1f}/100",
            'Sentiment Score': f"{result['sentiment_score']:.1f}/100",
            'Current Price': f"₹{result.get('current_price', 'N/A')}",
            'PE Ratio': result.get('pe_ratio', 'N/A'),
            'Market Cap': result.get('market_cap', 'N/A'),
            'News Sentiment': result.get('avg_sentiment', 'N/A')
        })
    
    df = pd.DataFrame(display_data)
    
    # Style the dataframe
    def style_recommendation(val):
        if val == 'BUY':
            return 'background-color: #d4edda; color: #155724'
        elif val == 'SELL':
            return 'background-color: #f8d7da; color: #721c24'
        else:
            return 'background-color: #fff3cd; color: #856404'
    
    styled_df = df.style.applymap(style_recommendation, subset=['Recommendation'])
    st.dataframe(styled_df, use_container_width=True)
    
    # Top recommendations
    st.markdown("### 🏆 Top 3 Recommendations")
    
    for i, result in enumerate(results_sorted[:3]):
        with st.expander(f"#{i+1} {result['company_name']} ({result['ticker']}) - {result['recommendation']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📊 Fundamental Analysis**")
                st.write(f"• PE Ratio: {result.get('pe_ratio', 'N/A')}")
                st.write(f"• PB Ratio: {result.get('pb_ratio', 'N/A')}")
                st.write(f"• ROE: {result.get('roe', 'N/A')}")
                st.write(f"• Market Cap: {result.get('market_cap', 'N/A')}")
            
            with col2:
                st.markdown("**📰 Sentiment Analysis**")
                st.write(f"• Average Sentiment: {result.get('avg_sentiment', 'N/A')}")
                st.write(f"• Positive News: {result.get('positive_count', 0)}")
                st.write(f"• Negative News: {result.get('negative_count', 0)}")
                st.write(f"• Total Articles: {result.get('total_articles', 0)}")
            
            st.markdown(f"**🎯 Final Score:** {result['overall_score']:.1f}/100")
            st.markdown(f"**💡 Reasoning:** {result.get('reasoning', 'Analysis completed successfully')}")
    
    # Download option
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download Analysis Results (CSV)",
        data=csv,
        file_name=f"stock_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

if __name__ == "__main__":
    main()
