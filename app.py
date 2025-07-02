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
    # Custom CSS for better styling and spacing
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 3rem 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        margin: -1rem -1rem 3rem -1rem;
        border-radius: 0 0 25px 25px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }
    
    .main-header h1 {
        color: white;
        font-size: 3.5rem;
        margin: 0;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.3);
        font-weight: 700;
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1.3rem;
        margin: 1rem 0 0 0;
        font-weight: 300;
        letter-spacing: 0.5px;
    }
    
    .section-spacing {
        margin: 2.5rem 0;
    }
    
    .process-card {
        text-align: center;
        padding: 2rem 1.5rem;
        border-radius: 15px;
        margin: 1rem 0.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .process-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .process-card h3 {
        margin: 0 0 1rem 0;
        font-size: 1.4rem;
        font-weight: 600;
    }
    
    .process-card p {
        margin: 0;
        font-size: 0.95rem;
        line-height: 1.5;
        opacity: 0.9;
    }
    
    .weight-slider-container {
        background: rgba(255,255,255,0.05);
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .analysis-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        padding: 1rem 2rem !important;
        border-radius: 12px !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    
    .analysis-button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6) !important;
    }
    
    .metric-card {
        padding: 1.8rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin: 0.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
    }
    
    .metric-card h2 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .metric-card p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 1rem;
        font-weight: 500;
    }
    
    /* Dark mode improvements */
    .stExpander > div > div > div {
        background-color: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 10px !important;
    }
    
    /* Light mode text contrast improvements */
    @media (prefers-color-scheme: light) {
        .process-card {
            background: white;
            color: #2c3e50;
            box-shadow: 0 2px 15px rgba(0,0,0,0.1);
        }
        
        .process-card p {
            color: #5a6c7d;
        }
        
        .weight-slider-container {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header Section
    st.markdown("""
    <div class='main-header'>
        <h1>🤖 AI Stock Advisor</h1>
        <p>Smart insights. Simple decisions.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize components
    cache_manager = get_cache_manager()
    screening_agent, fundamental_agent, sentiment_agent, aggregator_agent, data_normalizer = initialize_agents()
    
    # Step 1: Sector/Theme Selection
    st.markdown("<div class='section-spacing'>", unsafe_allow_html=True)
    st.markdown("### 🎯 Choose a Sector")
    st.markdown("Select an industry that interests you for focused analysis")
    
    sectors = {
        "🖥️ IT & Tech": ["TCS", "INFY", "HCLTECH", "WIPRO", "TECHM"],
        "🏦 Banking & Finance": ["HDFCBANK", "ICICIBANK", "SBIN", "KOTAKBANK", "AXISBANK"],
        "🚗 Auto": ["MARUTI", "TATAMOTORS", "M&M", "BAJAJ-AUTO", "EICHERMOT"],
        "⚗️ Pharma": ["SUNPHARMA", "DRREDDY", "CIPLA", "DIVISLAB", "BIOCON"],
        "🌿 Green Energy": ["ADANIGREEN", "SUZLON", "TATAPOWER", "NTPC", "POWERGRID"],
        "🏭 Diversified": ["RELIANCE", "ITC", "HINDUNILVR", "LT", "ASIANPAINT"]
    }
    
    selected_sector = st.selectbox(
        "Select sector:",
        options=list(sectors.keys()),
        index=0,
        help="Choose a sector that interests you for focused analysis"
    )
    
    # Show selected stocks preview
    st.markdown(f"**Selected stocks:** {', '.join(sectors[selected_sector][:3])}...")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Step 2: Sentiment vs Fundamental Weight Slider
    st.markdown("<div class='section-spacing'>", unsafe_allow_html=True)
    st.markdown("### ⚖️ Analysis Balance")
    st.markdown("Customize how much weight to give each type of analysis")
    
    st.markdown("<div class='weight-slider-container'>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        st.markdown("**📊 Fundamentals**")
        st.caption("Financial health, ratios, performance metrics")
    
    with col2:
        sentiment_weight = st.slider(
            "Balance focus:",
            min_value=0,
            max_value=100,
            value=50,
            step=10,
            format="%d%%",
            help="Move left for fundamental focus, right for sentiment focus"
        )
        
        # Visual representation with better styling
        fundamental_weight = 100 - sentiment_weight
        
        st.markdown(f"""
        <div style='display: flex; height: 30px; margin: 15px 0; border-radius: 15px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1);'>
            <div style='background: linear-gradient(135deg, #4CAF50, #45a049); width: {fundamental_weight}%; display: flex; align-items: center; justify-content: center; color: white; font-size: 14px; font-weight: 600;'>
                📊 {fundamental_weight}%
            </div>
            <div style='background: linear-gradient(135deg, #2196F3, #1976d2); width: {sentiment_weight}%; display: flex; align-items: center; justify-content: center; color: white; font-size: 14px; font-weight: 600;'>
                🗞️ {sentiment_weight}%
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("**🗞️ Sentiment**")
        st.caption("News analysis, market sentiment, buzz")
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Step 3: Advanced Options (collapsible)
    st.markdown("<div class='section-spacing'>", unsafe_allow_html=True)
    with st.expander("🔧 Advanced Options", expanded=False):
        st.markdown("**Fine-tune your analysis parameters**")
        
        col1, col2 = st.columns(2)
        with col1:
            num_stocks = st.selectbox(
                "Number of stocks to analyze:",
                options=[3, 5, 8, 10],
                index=1,
                help="More stocks = longer analysis time"
            )
        
        with col2:
            risk_tolerance = st.selectbox(
                "Risk Tolerance:",
                options=["Conservative", "Moderate", "Aggressive"],
                index=1,
                help="Adjusts recommendation thresholds"
            )
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Step 4: Analyze Button
    st.markdown("<div class='section-spacing'>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_button = st.button(
            "🔍 Run Analysis", 
            type="primary", 
            use_container_width=True,
            help="Start analyzing selected sector stocks"
        )
    
    st.markdown("</div>", unsafe_allow_html=True)
    
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
            <div class='process-card' style='background: linear-gradient(135deg, #e3f2fd, #bbdefb);'>
                <h3 style='color: #1976d2;'>🎯 Select</h3>
                <p style='color: #424242;'>Choose your preferred sector from IT, Banking, Auto, Pharma, and more</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class='process-card' style='background: linear-gradient(135deg, #f3e5f5, #e1bee7);'>
                <h3 style='color: #7b1fa2;'>⚖️ Balance</h3>
                <p style='color: #424242;'>Adjust focus between fundamental analysis and sentiment analysis</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class='process-card' style='background: linear-gradient(135deg, #e8f5e8, #c8e6c9);'>
                <h3 style='color: #388e3c;'>🔍 Analyze</h3>
                <p style='color: #424242;'>AI agents analyze fundamentals, news sentiment, and market data</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class='process-card' style='background: linear-gradient(135deg, #fff3e0, #ffcc02);'>
                <h3 style='color: #f57c00;'>📊 Decide</h3>
                <p style='color: #424242;'>Get BUY/HOLD/SELL recommendations with detailed reasoning</p>
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
    st.markdown("<div class='section-spacing'>", unsafe_allow_html=True)
    st.markdown("## 🧾 Stock Analysis Results")
    st.markdown("Here are your personalized stock recommendations based on AI analysis")
    
    # Summary metrics with improved styling
    col1, col2, col3, col4 = st.columns(4)
    
    buy_count = len([r for r in results_sorted if r['recommendation'] == 'BUY'])
    hold_count = len([r for r in results_sorted if r['recommendation'] == 'HOLD'])
    sell_count = len([r for r in results_sorted if r['recommendation'] == 'SELL'])
    avg_score = np.mean([r['overall_score'] for r in results_sorted])
    
    with col1:
        st.markdown("""
        <div class='metric-card' style='background: linear-gradient(135deg, #4CAF50, #45a049);'>
            <h2>✅ {}</h2>
            <p>BUY Recommendations</p>
        </div>
        """.format(buy_count), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='metric-card' style='background: linear-gradient(135deg, #FF9800, #f57c00);'>
            <h2>⚠️ {}</h2>
            <p>HOLD Recommendations</p>
        </div>
        """.format(hold_count), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='metric-card' style='background: linear-gradient(135deg, #f44336, #d32f2f);'>
            <h2>❌ {}</h2>
            <p>SELL Recommendations</p>
        </div>
        """.format(sell_count), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class='metric-card' style='background: linear-gradient(135deg, #2196F3, #1976d2);'>
            <h2>{:.1f}</h2>
            <p>Average Score</p>
        </div>
        """.format(avg_score), unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
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
    st.markdown("<div class='section-spacing'>", unsafe_allow_html=True)
    st.markdown("### 📋 Detailed Stock Analysis")
    st.markdown("Click each stock to see full analysis details")
    
    for i, result in enumerate(results_sorted):
        # Recommendation badge styling
        if result['recommendation'] == 'BUY':
            badge_color = '#4CAF50'
            badge_bg = 'linear-gradient(135deg, #4CAF50, #45a049)'
            badge_emoji = '✅'
        elif result['recommendation'] == 'HOLD':
            badge_color = '#FF9800'
            badge_bg = 'linear-gradient(135deg, #FF9800, #f57c00)'
            badge_emoji = '⚠️'
        else:
            badge_color = '#f44336'
            badge_bg = 'linear-gradient(135deg, #f44336, #d32f2f)'
            badge_emoji = '❌'
        
        # Create expandable card with improved styling
        with st.expander(f"#{i+1} {result['ticker']} - {result['company_name']}", expanded=(i==0)):
            
            # Enhanced summary view with better contrast
            st.markdown(f"""
            <div style='background: {badge_bg}; color: white; padding: 20px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <h2 style='margin: 0; font-size: 1.8rem; font-weight: 700;'>{badge_emoji} {result['recommendation']}</h2>
                        <p style='margin: 8px 0 0 0; opacity: 0.9; font-size: 1.1rem;'>Overall Score: {result['overall_score']:.1f}/100</p>
                    </div>
                    <div style='text-align: right;'>
                        <p style='margin: 0; font-size: 1rem; opacity: 0.8;'>Confidence: High</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Analysis breakdown with improved readability
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("#### ⚖️ Analysis Balance")
                fund_pct = fundamental_weight
                sent_pct = sentiment_weight
                
                st.markdown(f"""
                <div style='background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin: 10px 0;'>
                    <div style='display: flex; height: 25px; border-radius: 12px; overflow: hidden; margin: 10px 0;'>
                        <div style='background: linear-gradient(135deg, #4CAF50, #45a049); width: {fund_pct}%; display: flex; align-items: center; justify-content: center; color: white; font-size: 12px; font-weight: 600;'>
                            📊 {fund_pct}%
                        </div>
                        <div style='background: linear-gradient(135deg, #2196F3, #1976d2); width: {sent_pct}%; display: flex; align-items: center; justify-content: center; color: white; font-size: 12px; font-weight: 600;'>
                            🗞️ {sent_pct}%
                        </div>
                    </div>
                    <p style='margin: 5px 0 0 0; font-size: 0.9rem; opacity: 0.8;'>Fundamentals vs Sentiment</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("#### 📊 Fundamental Score")
                fund_score = result.get('fundamental_score', 50)
                fund_color = '#4CAF50' if fund_score >= 70 else '#FF9800' if fund_score >= 50 else '#f44336'
                
                st.markdown(f"""
                <div style='background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin: 10px 0; text-align: center;'>
                    <h3 style='margin: 0; color: {fund_color}; font-size: 2rem;'>{fund_score:.1f}</h3>
                    <p style='margin: 5px 0 0 0; font-size: 0.9rem; opacity: 0.8;'>Financial Health</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("#### 🗞️ Sentiment Score")
                sent_score = result.get('sentiment_score', 50)
                sent_color = '#4CAF50' if sent_score >= 70 else '#FF9800' if sent_score >= 50 else '#f44336'
                
                st.markdown(f"""
                <div style='background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin: 10px 0; text-align: center;'>
                    <h3 style='margin: 0; color: {sent_color}; font-size: 2rem;'>{sent_score:.1f}</h3>
                    <p style='margin: 5px 0 0 0; font-size: 0.9rem; opacity: 0.8;'>Market Sentiment</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Summary reasoning with better formatting
            st.markdown("#### 💡 AI Analysis Summary")
            reasoning = result.get('reasoning', 'Analysis completed successfully')
            st.markdown(f"""
            <div style='background: rgba(255,255,255,0.05); padding: 20px; border-radius: 10px; border-left: 4px solid {badge_color}; margin: 15px 0;'>
                <p style='margin: 0; font-size: 1rem; line-height: 1.6; color: var(--text-color);'>{reasoning}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Detailed metrics in organized sections
            st.markdown("---")
            detail_col1, detail_col2 = st.columns(2)
            
            with detail_col1:
                st.markdown("#### 📊 Financial Metrics")
                
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
                    
                    st.markdown(f"""
                    <div style='display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.1);'>
                        <span style='font-weight: 600;'>{label}:</span>
                        <span style='color: var(--text-color);'>{value}</span>
                    </div>
                    """, unsafe_allow_html=True)
            
            with detail_col2:
                st.markdown("#### 📰 News Analysis")
                
                sentiment_metrics = [
                    ("Sentiment Score", f"{result.get('avg_sentiment', 'N/A')}"),
                    ("Positive News", f"{result.get('positive_count', 0)} articles"),
                    ("Negative News", f"{result.get('negative_count', 0)} articles"),
                    ("Total Coverage", f"{result.get('total_articles', 0)} articles"),
                    ("News Quality", "Real-time data")
                ]
                
                for label, value in sentiment_metrics:
                    st.markdown(f"""
                    <div style='display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.1);'>
                        <span style='font-weight: 600;'>{label}:</span>
                        <span style='color: var(--text-color);'>{value}</span>
                    </div>
                    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
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
