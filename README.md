# 🤖 AI Stock Advisor

A sophisticated multi-agent AI system that provides intelligent stock analysis and investment recommendations for Indian market stocks. Built for hackathons and demonstrations, this system combines fundamental analysis with sentiment analysis to deliver actionable investment insights.

![AI Stock Advisor Screenshot](https://via.placeholder.com/800x400?text=AI+Stock+Advisor+Dashboard)

## 🌟 Features

- **🎯 Sector-Based Analysis**: Choose from IT, Banking, Auto, Pharma, Green Energy, and Diversified sectors
- **⚖️ Customizable Weighting**: Adjust balance between fundamental and sentiment analysis (0-100%)
- **📊 Real-Time Data**: Live financial metrics via yfinance API
- **📰 News Sentiment**: Latest market sentiment using NewsAPI + NLTK + spaCy
- **🔍 Interactive UI**: Modern Streamlit interface with expandable analysis cards
- **📈 Visual Charts**: Performance comparison charts using Plotly
- **💾 Smart Caching**: Two-tier caching system for optimal performance

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- NewsAPI key (free at [newsapi.org](https://newsapi.org))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ai-stock-advisor.git
   cd ai-stock-advisor
   ```

2. **Install dependencies**
   ```bash
   pip install streamlit pandas numpy yfinance requests beautifulsoup4 trafilatura nltk spacy plotly python-dateutil
   python -m spacy download en_core_web_sm
   ```

3. **Set up environment variables**
   ```bash
   export NEWS_API_KEY="your_newsapi_key_here"
   ```

4. **Run the application**
   ```bash
   streamlit run app.py --server.port 5000
   ```

5. **Open your browser** to `http://localhost:5000`

## 🏗️ Architecture

### Multi-Agent System

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Screening Agent │    │Fundamental Agent│    │ Sentiment Agent │
│                 │    │                 │    │                 │
│ • Sector stocks │    │ • yfinance API  │    │ • NewsAPI       │
│ • Stock lists   │    │ • PE, PB, ROE   │    │ • NLTK VADER    │
│ • Fallback data │    │ • Market cap    │    │ • spaCy NLP     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Aggregator Agent│
                    │                 │
                    │ • Score fusion  │
                    │ • Recommendations│
                    │ • BUY/HOLD/SELL │
                    └─────────────────┘
```

### Key Components

- **🎯 Screening Agent**: Curated stock lists by sector with fallback mechanisms
- **📊 Fundamental Agent**: Financial analysis using yfinance (PE, PB, ROE, etc.)
- **📰 Sentiment Agent**: News sentiment analysis using NewsAPI + NLP
- **🔧 Aggregator Agent**: Weighted score combination and final recommendations
- **💾 Cache Manager**: Two-tier caching (memory + file) for performance
- **📏 Data Normalizer**: Standardized 0-100 scoring across all metrics

## 📋 Usage Guide

### 1. Choose Your Sector
Select from predefined sectors:
- 🖥️ **IT & Tech**: TCS, INFY, HCLTECH, WIPRO, TECHM
- 🏦 **Banking**: HDFCBANK, ICICIBANK, SBI, KOTAKBANK, AXISBANK
- 🚗 **Auto**: MARUTI, TATAMOTORS, M&M, BAJAJ-AUTO, EICHERMOT
- ⚗️ **Pharma**: SUNPHARMA, DRREDDY, CIPLA, DIVISLAB, BIOCON
- 🌿 **Green Energy**: ADANIGREEN, SUZLON, TATAPOWER, NTPC, POWERGRID
- 🏭 **Diversified**: RELIANCE, ITC, HINDUNILVR, LT, ASIANPAINT

### 2. Set Analysis Balance
Use the interactive slider to adjust weighting:
- **Left (0%)**: Pure fundamental analysis
- **Center (50%)**: Balanced approach
- **Right (100%)**: Pure sentiment analysis

### 3. Advanced Options
- **Stock Count**: Analyze 3-10 stocks per sector
- **Risk Tolerance**: Conservative, Moderate, or Aggressive

### 4. Review Results
- **Summary Cards**: Quick overview of BUY/HOLD/SELL counts
- **Performance Chart**: Visual comparison of all analyzed stocks
- **Detailed Cards**: Expandable analysis with full metrics and reasoning

## 🔧 Configuration

### Environment Variables
```bash
NEWS_API_KEY=your_newsapi_key_here
```

### Streamlit Configuration
Create `.streamlit/config.toml`:
```toml
[server]
headless = true
address = "0.0.0.0"
port = 5000

[theme]
primaryColor = "#667eea"
backgroundColor = "#0e1117"
secondaryBackgroundColor = "#262730"
textColor = "#fafafa"
```

## 📊 API Reference

### External APIs Used

1. **yfinance**: Stock fundamental data (no authentication required)
   - Financial ratios (PE, PB, ROE)
   - Market cap and pricing data
   - Company information

2. **NewsAPI**: Latest news headlines (requires free API key)
   - Company-specific news search
   - Real-time market sentiment
   - Article content analysis

3. **NLTK**: Natural language processing
   - VADER sentiment analyzer
   - Text preprocessing and tokenization

4. **spaCy**: Advanced NLP pipeline
   - Named entity recognition
   - Advanced text analysis

## 🎯 Scoring System

### Fundamental Scoring (0-100)
- **PE Ratio**: Optimized for Indian market (15-25 range)
- **PB Ratio**: Book value assessment (1-3 range)
- **ROE**: Return on equity evaluation (>15% preferred)
- **Debt-to-Equity**: Financial stability (lower is better)
- **Profit Margins**: Operational efficiency

### Sentiment Scoring (0-100)
- **Article Coverage**: Number of recent news articles
- **Sentiment Ratio**: Positive vs negative news balance
- **Volatility**: Consistency of sentiment over time
- **Entity Recognition**: Company mention frequency

### Final Recommendations
- **BUY**: Score ≥ 70
- **HOLD**: Score 50-69
- **SELL**: Score < 50

## 🚧 Development

### Project Structure
```
ai-stock-advisor/
├── agents/
│   ├── screening_agent.py      # Stock discovery and selection
│   ├── fundamental_agent.py    # Financial analysis
│   ├── sentiment_agent.py      # News sentiment analysis
│   └── aggregator_agent.py     # Score aggregation
├── utils/
│   ├── cache_manager.py        # Caching system
│   └── data_normalizer.py      # Score normalization
├── .streamlit/
│   └── config.toml            # Streamlit configuration
├── app.py                     # Main application
├── requirements.txt           # Python dependencies
├── README.md                 # This file
└── replit.md                 # Project documentation
```

### Adding New Sectors
1. Update sector dictionary in `app.py`
2. Add corresponding stock tickers
3. Test with your desired stock count

### Customizing Scoring
1. Modify `DataNormalizer` class for different score ranges
2. Adjust recommendation thresholds in `AggregatorAgent`
3. Update sector-specific benchmarks

## 🔒 Security & Limitations

### Security Considerations
- API keys are handled via environment variables
- No financial advice disclaimer required
- Rate limiting implemented for external APIs
- Input validation for all user parameters

### Current Limitations
- **Demo Purpose**: Built for hackathons, not production trading
- **Indian Market Focus**: Optimized for NSE-listed stocks
- **API Dependencies**: Requires stable internet and valid API keys
- **No Real-time Trading**: Analysis only, no order execution
- **Cache TTL**: 1-hour cache may not reflect rapid market changes

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Add tests** (if applicable)
5. **Commit your changes**
   ```bash
   git commit -m 'Add amazing feature'
   ```
6. **Push to the branch**
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Open a Pull Request**

### Development Guidelines
- Follow PEP 8 style guidelines
- Add docstrings to all functions
- Update tests for new features
- Maintain backward compatibility
- Update documentation as needed

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **yfinance**: For providing free access to financial data
- **NewsAPI**: For real-time news sentiment data
- **Streamlit**: For the amazing web app framework
- **NLTK & spaCy**: For powerful NLP capabilities
- **Plotly**: For interactive data visualization

## 📞 Support

- **Issues**: Report bugs via [GitHub Issues](https://github.com/yourusername/ai-stock-advisor/issues)
- **Discussions**: Join conversations in [GitHub Discussions](https://github.com/yourusername/ai-stock-advisor/discussions)
- **Documentation**: Check the `replit.md` file for technical details

## ⚠️ Disclaimer

This tool is for educational and demonstration purposes only. It does not constitute financial advice. Always consult with qualified financial advisors before making investment decisions. Past performance does not guarantee future results.

---

**Built with ❤️ for the developer community**