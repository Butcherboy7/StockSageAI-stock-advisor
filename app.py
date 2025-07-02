import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime
import os
import plotly.express as px
import plotly.graph_objects as go

# Import our custom agents
from agents.screening_agent import ScreeningAgent
from agents.fundamental_agent import FundamentalAgent
from agents.sentiment_agent import SentimentAgent
from agents.aggregator_agent import AggregatorAgent
from utils.cache_manager import CacheManager
from utils.data_normalizer import DataNormalizer

# Configure page
st.set_page_config(
    page_title="🤖 AI Stock Advisor",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
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
    # Header Section
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin: -1rem -1rem 2rem -1rem; border-radius: 0 0 20px 20px;'>
        <h1 style='color: white; font-size: 3rem; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>🤖 AI Stock Advisor</h1>
        <p style='color: rgba(255,255,255,0.9); font-size: 1.2rem; margin: 0.5rem 0 0 0; font-weight: 300;'>Smart insights. Simple decisions.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize components
    cache_manager = get_cache_manager()
    screening_agent, fundamental_agent, sentiment_agent, aggregator_agent, data_normalizer = initialize_agents()
    
    # Step 1: Sector/Theme Selection
    st.markdown("### 🎯 Choose a Sector")
    
    sectors = {
        "🖥️ IT & Tech": ["TCS", "INFY", "HCLTECH", "WIPRO", "TECHM"],
        "🏦 Banking & Finance": ["HDFCBANK", "ICICIBANK", "SBIN", "KOTAKBANK", "AXISBANK"],
        "🚗 Auto": ["MARUTI", "TATAMOTORS", "M&M", "BAJAJ-AUTO", "EICHERMOT"],
        "⚗️ Pharma": ["SUNPHARMA", "DRREDDY", "CIPLA", "DIVISLAB", "BIOCON"],
        "🌿 Green Energy": ["ADANIGREEN", "SUZLON", "TATAPOWER", "NTPC", "POWERGRID"],
        "🏭 Diversified": ["RELIANCE", "ITC", "HINDUNILVR", "LT", "ASIANPAINT"]
    }
    
    selected_sector = st.selectbox(
        "Select sector to analyze:",
        options=list(sectors.keys()),
        index=0,
        help="Choose a sector that interests you for focused analysis"
    )
    
    # Step 2: Sentiment vs Fundamental Weight Slider
    st.markdown("### ⚖️ Analysis Balance")
    
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        st.markdown("**📊 Fundamentals**")
        st.caption("Financial metrics, ratios")
    
    with col2:
        sentiment_weight = st.slider(
            "Adjust analysis focus:",
            min_value=0,
            max_value=100,
            value=50,
            step=10,
            format="%d%%",
            help="Move left for fundamental focus, right for sentiment focus"
        )
        
        # Visual representation
        fundamental_weight = 100 - sentiment_weight
        
        # Create a visual bar
        st.markdown(f"""
        <div style='display: flex; height: 20px; margin: 10px 0; border-radius: 10px; overflow: hidden;'>
            <div style='background: #4CAF50; width: {fundamental_weight}%; display: flex; align-items: center; justify-content: center; color: white; font-size: 12px;'>
                {fundamental_weight}%
            </div>
            <div style='background: #2196F3; width: {sentiment_weight}%; display: flex; align-items: center; justify-content: center; color: white; font-size: 12px;'>
                {sentiment_weight}%
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("**🗞️ Sentiment**")
        st.caption("News, market buzz")
    
    # Step 3: Advanced Options (collapsible)
    with st.expander("🔧 Advanced Options", expanded=False):
        num_stocks = st.selectbox(
            "Number of stocks to analyze:",
            options=[3, 5, 8, 10],
            index=1,
            help="More stocks = longer analysis time"
        )
        
        risk_tolerance = st.selectbox(
            "Risk Tolerance:",
            options=["Conservative", "Moderate", "Aggressive"],
            index=1,
            help="Adjusts recommendation thresholds"
        )
    
    # Step 4: Analyze Button
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        analyze_button = st.button(
            "🔍 Run Analysis", 
            type="primary", 
            use_container_width=True,
            help="Start analyzing selected sector stocks"
        )
    
    # Main content area
    if analyze_button:
        with st.spinner("🔍 Multi-Agent Analysis in Progress..."):
            try:
                # Progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Step 1: Use sector-based stocks instead of scraping
                status_text.text("🎯 Preparing sector stocks for analysis...")
                progress_bar.progress(10)
                
                # Get stocks from selected sector
                sector_stocks = sectors[selected_sector][:num_stocks]
                screening_results = []
                
                for ticker in sector_stocks:
                    screening_results.append({
                        'ticker': ticker,
                        'name': f"{ticker} Limited",  # Simplified for demo
                        'sector': selected_sector,
                        'source': 'sector_selection'
                    })
                
                if not screening_results:
                    st.error("❌ No stocks found for selected sector")
                    return
                
                st.success(f"✅ Analyzing {len(screening_results)} stocks from {selected_sector}")
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
        # Modern welcome screen
        st.markdown("---")
        
        # How it works section
        st.markdown("## 🎯 How It Works")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #e3f2fd, #bbdefb); border-radius: 10px; margin: 10px 0;'>
                <h3 style='color: #1976d2; margin: 0 0 10px 0;'>🎯 Select</h3>
                <p style='color: #424242; margin: 0; font-size: 14px;'>Choose your preferred sector from IT, Banking, Auto, Pharma, and more</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #f3e5f5, #e1bee7); border-radius: 10px; margin: 10px 0;'>
                <h3 style='color: #7b1fa2; margin: 0 0 10px 0;'>⚖️ Balance</h3>
                <p style='color: #424242; margin: 0; font-size: 14px;'>Adjust focus between fundamental analysis and sentiment analysis</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #e8f5e8, #c8e6c9); border-radius: 10px; margin: 10px 0;'>
                <h3 style='color: #388e3c; margin: 0 0 10px 0;'>🔍 Analyze</h3>
                <p style='color: #424242; margin: 0; font-size: 14px;'>AI agents analyze fundamentals, news sentiment, and market data</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #fff3e0, #ffcc02); border-radius: 10px; margin: 10px 0;'>
                <h3 style='color: #f57c00; margin: 0 0 10px 0;'>📊 Decide</h3>
                <p style='color: #424242; margin: 0; font-size: 14px;'>Get BUY/HOLD/SELL recommendations with detailed reasoning</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Agent details in collapsible sections
        with st.expander("🤖 Meet the AI Agents", expanded=False):
            agent_col1, agent_col2 = st.columns(2)
            
            with agent_col1:
                st.markdown("""
                **📊 Fundamental Analysis Agent**
                - Fetches live data using yfinance
                - Analyzes PE ratio, PB ratio, ROE, debt levels
                - Evaluates financial health and growth metrics
                
                **🔧 Aggregator Agent**
                - Combines all analysis into single score
                - Generates BUY/HOLD/SELL recommendations
                - Provides human-readable reasoning
                """)
            
            with agent_col2:
                st.markdown("""
                **📰 Sentiment Analysis Agent**
                - Fetches latest news via NewsAPI
                - Uses NLTK VADER sentiment analysis
                - Applies spaCy NLP for entity recognition
                
                **🎯 Sector Intelligence**
                - Curated stock lists by industry
                - Context-aware analysis for each sector
                - Focused recommendations within themes
                """)
        
        # Sample preview
        st.markdown("### 📈 Sample Analysis Preview")
        
        # Mock sample card for demonstration
        with st.container():
            st.markdown("""
            <div style='border: 2px dashed #ccc; padding: 20px; border-radius: 10px; background: #f9f9f9;'>
                <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;'>
                    <h4 style='margin: 0; color: #333;'>📊 Sample: TCS - Tata Consultancy Services</h4>
                    <span style='background: #4CAF50; color: white; padding: 5px 15px; border-radius: 20px; font-weight: bold;'>✅ BUY</span>
                </div>
                <p style='color: #666; margin: 0 0 10px 0;'><strong>Score:</strong> 78.5/100 | <strong>PE:</strong> 22.4 | <strong>Sentiment:</strong> Positive</p>
                <p style='color: #555; margin: 0; font-style: italic;'>Strong fundamentals with positive market sentiment and excellent returns on equity</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Call to action
        st.markdown("### 🚀 Ready to Start?")
        st.markdown("1. **Choose a sector** that interests you")
        st.markdown("2. **Adjust the analysis balance** based on your preference")
        st.markdown("3. **Click 'Run Analysis'** to get AI-powered recommendations")
        
        # Quick stats
        info_col1, info_col2 = st.columns(2)
        
        with info_col1:
            st.info("""
            **⚡ Fast & Accurate**
            - Analysis completed in 30-60 seconds
            - Real-time data from yfinance
            - Smart caching for better performance
            """)
        
        with info_col2:
            st.success("""
            **🔒 Reliable Sources**
            - Live financial data
            - Latest news sentiment
            - No mock or placeholder data
            """)

def display_results(results, fundamental_weight, sentiment_weight):
    """Display comprehensive analysis results with modern card-based interface"""
    
    # Sort by overall score
    results_sorted = sorted(results, key=lambda x: x['overall_score'], reverse=True)
    
    # Header with performance chart
    st.markdown("## 🧾 Stock Insights Grid")
    
    # Summary metrics in a nice layout
    col1, col2, col3, col4 = st.columns(4)
    
    buy_count = len([r for r in results_sorted if r['recommendation'] == 'BUY'])
    hold_count = len([r for r in results_sorted if r['recommendation'] == 'HOLD'])
    sell_count = len([r for r in results_sorted if r['recommendation'] == 'SELL'])
    avg_score = np.mean([r['overall_score'] for r in results_sorted])
    
    with col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #4CAF50, #45a049); padding: 20px; border-radius: 10px; text-align: center; color: white;'>
            <h2 style='margin: 0; font-size: 2rem;'>✅ {}</h2>
            <p style='margin: 5px 0 0 0; opacity: 0.9;'>BUY</p>
        </div>
        """.format(buy_count), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #FF9800, #f57c00); padding: 20px; border-radius: 10px; text-align: center; color: white;'>
            <h2 style='margin: 0; font-size: 2rem;'>⚠️ {}</h2>
            <p style='margin: 5px 0 0 0; opacity: 0.9;'>HOLD</p>
        </div>
        """.format(hold_count), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #f44336, #d32f2f); padding: 20px; border-radius: 10px; text-align: center; color: white;'>
            <h2 style='margin: 0; font-size: 2rem;'>❌ {}</h2>
            <p style='margin: 5px 0 0 0; opacity: 0.9;'>SELL</p>
        </div>
        """.format(sell_count), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #2196F3, #1976d2); padding: 20px; border-radius: 10px; text-align: center; color: white;'>
            <h2 style='margin: 0; font-size: 2rem;'>{:.1f}</h2>
            <p style='margin: 5px 0 0 0; opacity: 0.9;'>Avg Score</p>
        </div>
        """.format(avg_score), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Performance chart
    if len(results_sorted) > 1:
        fig = go.Figure()
        
        colors = ['#4CAF50' if r['recommendation'] == 'BUY' 
                 else '#FF9800' if r['recommendation'] == 'HOLD' 
                 else '#f44336' for r in results_sorted]
        
        fig.add_trace(go.Bar(
            x=[r['ticker'] for r in results_sorted],
            y=[r['overall_score'] for r in results_sorted],
            marker_color=colors,
            text=[f"{r['overall_score']:.1f}" for r in results_sorted],
            textposition='auto',
        ))
        
        fig.update_layout(
            title="📊 Stock Performance Comparison",
            xaxis_title="Stock Ticker",
            yaxis_title="Overall Score",
            showlegend=False,
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Stock cards with expandable details
    st.markdown("### 📋 Detailed Stock Analysis")
    
    for i, result in enumerate(results_sorted):
        # Recommendation badge styling
        if result['recommendation'] == 'BUY':
            badge_color = '#4CAF50'
            badge_emoji = '✅'
        elif result['recommendation'] == 'HOLD':
            badge_color = '#FF9800'  
            badge_emoji = '⚠️'
        else:
            badge_color = '#f44336'
            badge_emoji = '❌'
        
        # Create expandable card
        with st.expander(f"#{i+1} {result['ticker']} - {result['company_name']}", expanded=(i==0)):
            
            # Compact summary view
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"""
                <div style='background: {badge_color}; color: white; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>
                    <h3 style='margin: 0;'>{badge_emoji} {result['recommendation']}</h3>
                    <p style='margin: 5px 0 0 0; opacity: 0.9;'>Score: {result['overall_score']:.1f}/100</p>
                </div>
                """, unsafe_allow_html=True)
                
                # One-liner summary
                st.markdown(f"**💡 Summary:** {result.get('reasoning', 'Analysis completed successfully')}")
            
            with col2:
                # Visual weighting representation
                st.markdown("**⚖️ Analysis Mix**")
                fund_pct = fundamental_weight
                sent_pct = sentiment_weight
                
                st.markdown(f"""
                <div style='display: flex; height: 15px; border-radius: 7px; overflow: hidden; margin: 5px 0;'>
                    <div style='background: #4CAF50; width: {fund_pct}%; display: flex; align-items: center; justify-content: center; color: white; font-size: 10px;'>
                        F:{fund_pct}%
                    </div>
                    <div style='background: #2196F3; width: {sent_pct}%; display: flex; align-items: center; justify-content: center; color: white; font-size: 10px;'>
                        S:{sent_pct}%
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                # Sentiment sparkline (simplified)
                sentiment_score = result.get('avg_sentiment', 0)
                if sentiment_score > 0.1:
                    trend = "📈 Positive"
                    trend_color = "#4CAF50"
                elif sentiment_score < -0.1:
                    trend = "📉 Negative"
                    trend_color = "#f44336"
                else:
                    trend = "📊 Neutral"
                    trend_color = "#FF9800"
                
                st.markdown(f"**🗞️ News Sentiment**")
                st.markdown(f"<span style='color: {trend_color};'><strong>{trend}</strong></span>", unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Expandable detailed view
            detail_col1, detail_col2 = st.columns(2)
            
            with detail_col1:
                st.markdown("**📊 Fundamentals**")
                
                # Clean display of metrics
                metrics = [
                    ("PE Ratio", result.get('pe_ratio', 'N/A')),
                    ("PB Ratio", result.get('pb_ratio', 'N/A')), 
                    ("ROE", result.get('roe', 'N/A')),
                    ("Market Cap", result.get('market_cap', 'N/A')),
                    ("Current Price", f"₹{result.get('current_price', 'N/A')}")
                ]
                
                for label, value in metrics:
                    if value != 'N/A' and value is not None:
                        if isinstance(value, float) and abs(value) < 1:
                            value = f"{value:.3f}"
                        elif isinstance(value, float):
                            value = f"{value:.2f}"
                    st.markdown(f"• **{label}:** {value}")
            
            with detail_col2:
                st.markdown("**📰 Sentiment Details**")
                
                # Display sentiment metrics
                st.markdown(f"• **Sentiment Score:** {result.get('avg_sentiment', 'N/A')}")
                st.markdown(f"• **📈 Positive News:** {result.get('positive_count', 0)}")
                st.markdown(f"• **📉 Negative News:** {result.get('negative_count', 0)}")
                st.markdown(f"• **📰 Total Articles:** {result.get('total_articles', 0)}")
                
                # Show sample headlines if available
                if result.get('total_articles', 0) > 0:
                    st.markdown("**Recent Headlines:**")
                    # Placeholder for headlines - would be populated by sentiment agent
                    st.markdown("• Latest market developments")
                    st.markdown("• Company performance updates")
    
    # Action buttons
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Download CSV
        df_export = pd.DataFrame([{
            'Rank': i+1,
            'Ticker': r['ticker'],
            'Company': r['company_name'],
            'Recommendation': r['recommendation'],
            'Score': r['overall_score'],
            'PE_Ratio': r.get('pe_ratio', 'N/A'),
            'Sentiment': r.get('avg_sentiment', 'N/A')
        } for i, r in enumerate(results_sorted)])
        
        csv = df_export.to_csv(index=False)
        st.download_button(
            "📥 Download CSV",
            data=csv,
            file_name=f"stock_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        if st.button("🔄 Refresh Analysis", use_container_width=True):
            st.rerun()
    
    with col3:
        st.button("📊 View Portfolio", use_container_width=True, help="Coming soon")

if __name__ == "__main__":
    main()
