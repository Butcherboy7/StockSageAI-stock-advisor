import yfinance as yf
import pandas as pd
from typing import Dict, Optional
import time

class FundamentalAgent:
    """Agent responsible for fundamental analysis using yfinance"""
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = 300  # 5 minutes cache
    
    def analyze_stock(self, ticker: str) -> Dict:
        """
        Perform fundamental analysis on a stock
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary containing fundamental metrics
        """
        try:
            # Add .NS suffix for Indian stocks if not present
            yf_ticker = ticker if '.NS' in ticker else f"{ticker}.NS"
            
            # Check cache first
            cache_key = f"fundamental_{yf_ticker}"
            if self._is_cached(cache_key):
                return self.cache[cache_key]['data']
            
            # Fetch stock data
            stock = yf.Ticker(yf_ticker)
            
            # Get basic info
            info = stock.info
            
            # Get financial data
            financials = self._get_safe_financials(stock)
            
            # Calculate fundamental metrics
            fundamental_data = {
                'ticker': ticker,
                'yf_ticker': yf_ticker,
                'company_name': info.get('longName', info.get('shortName', ticker)),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': self._format_large_number(info.get('marketCap')),
                'current_price': info.get('currentPrice', info.get('regularMarketPrice')),
                'currency': info.get('currency', 'INR'),
                
                # Valuation ratios
                'pe_ratio': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'pb_ratio': info.get('priceToBook'),
                'ps_ratio': info.get('priceToSalesTrailing12Months'),
                'peg_ratio': info.get('pegRatio'),
                
                # Profitability metrics
                'roe': info.get('returnOnEquity'),
                'roa': info.get('returnOnAssets'),
                'profit_margin': info.get('profitMargins'),
                'operating_margin': info.get('operatingMargins'),
                'gross_margin': info.get('grossMargins'),
                
                # Financial health
                'debt_to_equity': info.get('debtToEquity'),
                'current_ratio': info.get('currentRatio'),
                'quick_ratio': info.get('quickRatio'),
                'total_cash': self._format_large_number(info.get('totalCash')),
                'total_debt': self._format_large_number(info.get('totalDebt')),
                
                # Growth metrics
                'revenue_growth': info.get('revenueGrowth'),
                'earnings_growth': info.get('earningsGrowth'),
                'book_value': info.get('bookValue'),
                
                # Dividend information
                'dividend_yield': info.get('dividendYield'),
                'payout_ratio': info.get('payoutRatio'),
                'dividend_rate': info.get('dividendRate'),
                
                # Trading metrics
                'beta': info.get('beta'),
                'volume': info.get('volume'),
                'avg_volume': info.get('averageVolume'),
                '52_week_high': info.get('fiftyTwoWeekHigh'),
                '52_week_low': info.get('fiftyTwoWeekLow'),
                
                # Additional metrics from financials
                **financials,
                
                'analysis_timestamp': time.time(),
                'data_quality': self._assess_data_quality(info)
            }
            
            # Cache the results
            self._cache_data(cache_key, fundamental_data)
            
            return fundamental_data
            
        except Exception as e:
            print(f"Error analyzing {ticker}: {e}")
            return {
                'ticker': ticker,
                'error': str(e),
                'analysis_timestamp': time.time(),
                'data_quality': 'error'
            }
    
    def _get_safe_financials(self, stock) -> Dict:
        """Safely extract financial data from yfinance"""
        try:
            # Get quarterly and annual financials
            quarterly_financials = stock.quarterly_financials
            annual_financials = stock.financials
            
            financials_data = {}
            
            # Extract key financial metrics if available
            if not quarterly_financials.empty:
                try:
                    # Most recent quarter
                    recent_quarter = quarterly_financials.columns[0]
                    
                    # Revenue (try different possible names)
                    revenue_keys = ['Total Revenue', 'Revenue', 'Net Sales']
                    for key in revenue_keys:
                        if key in quarterly_financials.index:
                            financials_data['quarterly_revenue'] = quarterly_financials.loc[key, recent_quarter]
                            break
                    
                    # Net Income
                    income_keys = ['Net Income', 'Net Income Common Stockholders']
                    for key in income_keys:
                        if key in quarterly_financials.index:
                            financials_data['quarterly_net_income'] = quarterly_financials.loc[key, recent_quarter]
                            break
                            
                except Exception as e:
                    print(f"Error extracting quarterly financials: {e}")
            
            # Extract annual data if available
            if not annual_financials.empty:
                try:
                    recent_year = annual_financials.columns[0]
                    
                    # Annual revenue
                    for key in ['Total Revenue', 'Revenue', 'Net Sales']:
                        if key in annual_financials.index:
                            financials_data['annual_revenue'] = annual_financials.loc[key, recent_year]
                            break
                    
                    # Annual net income
                    for key in ['Net Income', 'Net Income Common Stockholders']:
                        if key in annual_financials.index:
                            financials_data['annual_net_income'] = annual_financials.loc[key, recent_year]
                            break
                            
                except Exception as e:
                    print(f"Error extracting annual financials: {e}")
            
            return financials_data
            
        except Exception as e:
            print(f"Error getting financials: {e}")
            return {}
    
    def _format_large_number(self, value) -> str:
        """Format large numbers in a readable format"""
        if value is None:
            return 'N/A'
        
        try:
            value = float(value)
            if value >= 1e12:
                return f"₹{value/1e12:.2f}T"
            elif value >= 1e9:
                return f"₹{value/1e9:.2f}B"
            elif value >= 1e7:
                return f"₹{value/1e7:.2f}Cr"
            elif value >= 1e5:
                return f"₹{value/1e5:.2f}L"
            else:
                return f"₹{value:,.0f}"
        except:
            return str(value)
    
    def _assess_data_quality(self, info: Dict) -> str:
        """Assess the quality of data retrieved"""
        key_metrics = ['trailingPE', 'priceToBook', 'returnOnEquity', 'marketCap']
        available_metrics = sum(1 for metric in key_metrics if info.get(metric) is not None)
        
        if available_metrics >= 3:
            return 'good'
        elif available_metrics >= 2:
            return 'fair'
        else:
            return 'poor'
    
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
    
    def get_peer_comparison(self, ticker: str, sector: str = None) -> Dict:
        """Get peer comparison data (placeholder for future enhancement)"""
        return {
            'peer_analysis': 'Not implemented in MVP',
            'sector_average_pe': 'N/A',
            'relative_valuation': 'N/A'
        }
    
    def calculate_intrinsic_value(self, ticker: str) -> Dict:
        """Calculate intrinsic value using DCF (simplified for MVP)"""
        try:
            fundamental_data = self.analyze_stock(ticker)
            
            # Simplified intrinsic value calculation
            # This is a basic implementation for demo purposes
            pe_ratio = fundamental_data.get('pe_ratio')
            current_price = fundamental_data.get('current_price')
            
            if pe_ratio and current_price:
                # Simple fair value estimate based on average PE
                average_market_pe = 20  # Assumption for Indian market
                estimated_fair_value = current_price * (average_market_pe / pe_ratio)
                
                return {
                    'current_price': current_price,
                    'estimated_fair_value': estimated_fair_value,
                    'upside_potential': ((estimated_fair_value - current_price) / current_price) * 100,
                    'valuation': 'undervalued' if estimated_fair_value > current_price else 'overvalued'
                }
            
            return {'error': 'Insufficient data for valuation'}
            
        except Exception as e:
            return {'error': str(e)}
