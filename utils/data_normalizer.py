import numpy as np
from typing import Dict, List, Any, Optional, Union

class DataNormalizer:
    """Utility class for normalizing and scaling data across different agents"""
    
    def __init__(self):
        # Define normalization ranges and benchmarks for Indian market
        self.fundamental_benchmarks = {
            'pe_ratio': {'excellent': 15, 'good': 20, 'fair': 25, 'poor': 35},
            'pb_ratio': {'excellent': 1.5, 'good': 3, 'fair': 5, 'poor': 8},
            'roe': {'excellent': 0.20, 'good': 0.15, 'fair': 0.10, 'poor': 0.05},
            'debt_to_equity': {'excellent': 0.3, 'good': 0.6, 'fair': 1.0, 'poor': 1.5},
            'profit_margin': {'excellent': 0.20, 'good': 0.10, 'fair': 0.05, 'poor': 0.02}
        }
        
        self.sentiment_ranges = {
            'very_positive': 0.5,
            'positive': 0.1,
            'neutral': 0.05,
            'negative': -0.1,
            'very_negative': -0.5
        }
    
    def normalize_fundamental_score(self, fundamental_data: Dict) -> float:
        """
        Normalize fundamental data to a 0-100 score
        
        Args:
            fundamental_data: Dictionary containing fundamental metrics
            
        Returns:
            Normalized score between 0-100
        """
        try:
            if not fundamental_data or fundamental_data.get('error'):
                return 50.0  # Neutral score for missing data
            
            score = 0.0
            total_weight = 0.0
            
            # PE Ratio (Weight: 20%)
            pe_score = self._normalize_pe_ratio(fundamental_data.get('pe_ratio'))
            if pe_score is not None:
                score += pe_score * 0.20
                total_weight += 0.20
            
            # PB Ratio (Weight: 15%)
            pb_score = self._normalize_pb_ratio(fundamental_data.get('pb_ratio'))
            if pb_score is not None:
                score += pb_score * 0.15
                total_weight += 0.15
            
            # ROE (Weight: 25%)
            roe_score = self._normalize_roe(fundamental_data.get('roe'))
            if roe_score is not None:
                score += roe_score * 0.25
                total_weight += 0.25
            
            # Debt to Equity (Weight: 15%)
            debt_score = self._normalize_debt_to_equity(fundamental_data.get('debt_to_equity'))
            if debt_score is not None:
                score += debt_score * 0.15
                total_weight += 0.15
            
            # Profit Margin (Weight: 15%)
            margin_score = self._normalize_profit_margin(fundamental_data.get('profit_margin'))
            if margin_score is not None:
                score += margin_score * 0.15
                total_weight += 0.15
            
            # Revenue Growth (Weight: 10%)
            growth_score = self._normalize_revenue_growth(fundamental_data.get('revenue_growth'))
            if growth_score is not None:
                score += growth_score * 0.10
                total_weight += 0.10
            
            # Normalize by actual weight used
            if total_weight > 0:
                final_score = (score / total_weight) * 100
            else:
                final_score = 50.0  # Default neutral score
            
            return max(0, min(100, final_score))
            
        except Exception as e:
            print(f"Error normalizing fundamental score: {e}")
            return 50.0
    
    def normalize_sentiment_score(self, sentiment_data: Dict) -> float:
        """
        Normalize sentiment data to a 0-100 score
        
        Args:
            sentiment_data: Dictionary containing sentiment metrics
            
        Returns:
            Normalized score between 0-100
        """
        try:
            if not sentiment_data or sentiment_data.get('error'):
                return 50.0  # Neutral score for missing data
            
            score = 50.0  # Start with neutral
            
            # Average sentiment (Weight: 50%)
            avg_sentiment = sentiment_data.get('avg_sentiment', 0.0)
            if avg_sentiment is not None:
                # Convert VADER score (-1 to 1) to contribution (-25 to +25)
                sentiment_contribution = avg_sentiment * 25
                score += sentiment_contribution
            
            # Article coverage (Weight: 20%)
            total_articles = sentiment_data.get('total_articles', 0)
            coverage_score = self._normalize_article_coverage(total_articles)
            score += (coverage_score - 50) * 0.20
            
            # Positive/Negative ratio (Weight: 20%)
            positive_count = sentiment_data.get('positive_count', 0)
            negative_count = sentiment_data.get('negative_count', 0)
            ratio_score = self._normalize_sentiment_ratio(positive_count, negative_count)
            score += (ratio_score - 50) * 0.20
            
            # Sentiment consistency (Weight: 10%)
            volatility = sentiment_data.get('sentiment_volatility', 0.0)
            consistency_score = self._normalize_sentiment_consistency(volatility)
            score += (consistency_score - 50) * 0.10
            
            return max(0, min(100, score))
            
        except Exception as e:
            print(f"Error normalizing sentiment score: {e}")
            return 50.0
    
    def _normalize_pe_ratio(self, pe_ratio: Optional[float]) -> Optional[float]:
        """Normalize PE ratio to 0-100 scale"""
        if pe_ratio is None or pe_ratio <= 0:
            return None
        
        benchmarks = self.fundamental_benchmarks['pe_ratio']
        
        if pe_ratio <= benchmarks['excellent']:
            return 100
        elif pe_ratio <= benchmarks['good']:
            return 85
        elif pe_ratio <= benchmarks['fair']:
            return 65
        elif pe_ratio <= benchmarks['poor']:
            return 40
        else:
            return max(0, 40 - (pe_ratio - benchmarks['poor']) * 2)
    
    def _normalize_pb_ratio(self, pb_ratio: Optional[float]) -> Optional[float]:
        """Normalize PB ratio to 0-100 scale"""
        if pb_ratio is None or pb_ratio <= 0:
            return None
        
        benchmarks = self.fundamental_benchmarks['pb_ratio']
        
        if pb_ratio <= benchmarks['excellent']:
            return 100
        elif pb_ratio <= benchmarks['good']:
            return 80
        elif pb_ratio <= benchmarks['fair']:
            return 60
        elif pb_ratio <= benchmarks['poor']:
            return 30
        else:
            return max(0, 30 - (pb_ratio - benchmarks['poor']) * 5)
    
    def _normalize_roe(self, roe: Optional[float]) -> Optional[float]:
        """Normalize ROE to 0-100 scale"""
        if roe is None:
            return None
        
        # Handle both decimal (0.15) and percentage (15) formats
        roe_value = roe if roe <= 1 else roe / 100
        benchmarks = self.fundamental_benchmarks['roe']
        
        if roe_value >= benchmarks['excellent']:
            return 100
        elif roe_value >= benchmarks['good']:
            return 85
        elif roe_value >= benchmarks['fair']:
            return 65
        elif roe_value >= benchmarks['poor']:
            return 40
        elif roe_value > 0:
            return 20
        else:
            return 0
    
    def _normalize_debt_to_equity(self, debt_to_equity: Optional[float]) -> Optional[float]:
        """Normalize Debt-to-Equity ratio to 0-100 scale (lower is better)"""
        if debt_to_equity is None:
            return None
        
        benchmarks = self.fundamental_benchmarks['debt_to_equity']
        
        if debt_to_equity <= benchmarks['excellent']:
            return 100
        elif debt_to_equity <= benchmarks['good']:
            return 80
        elif debt_to_equity <= benchmarks['fair']:
            return 60
        elif debt_to_equity <= benchmarks['poor']:
            return 40
        else:
            return max(0, 40 - (debt_to_equity - benchmarks['poor']) * 10)
    
    def _normalize_profit_margin(self, profit_margin: Optional[float]) -> Optional[float]:
        """Normalize profit margin to 0-100 scale"""
        if profit_margin is None:
            return None
        
        # Handle both decimal (0.15) and percentage (15) formats
        margin_value = profit_margin if profit_margin <= 1 else profit_margin / 100
        benchmarks = self.fundamental_benchmarks['profit_margin']
        
        if margin_value >= benchmarks['excellent']:
            return 100
        elif margin_value >= benchmarks['good']:
            return 85
        elif margin_value >= benchmarks['fair']:
            return 65
        elif margin_value >= benchmarks['poor']:
            return 40
        elif margin_value > 0:
            return 20
        else:
            return 0
    
    def _normalize_revenue_growth(self, revenue_growth: Optional[float]) -> Optional[float]:
        """Normalize revenue growth to 0-100 scale"""
        if revenue_growth is None:
            return None
        
        # Handle both decimal (0.15) and percentage (15) formats
        growth_value = revenue_growth if abs(revenue_growth) <= 1 else revenue_growth / 100
        
        if growth_value >= 0.30:  # 30%+ growth
            return 100
        elif growth_value >= 0.20:  # 20%+ growth
            return 90
        elif growth_value >= 0.10:  # 10%+ growth
            return 75
        elif growth_value >= 0.05:  # 5%+ growth
            return 60
        elif growth_value >= 0:     # Positive growth
            return 50
        elif growth_value >= -0.05: # Small decline
            return 40
        elif growth_value >= -0.10: # Moderate decline
            return 25
        else:                       # Large decline
            return 0
    
    def _normalize_article_coverage(self, total_articles: int) -> float:
        """Normalize article coverage to 0-100 scale"""
        if total_articles >= 15:
            return 100
        elif total_articles >= 10:
            return 85
        elif total_articles >= 5:
            return 70
        elif total_articles >= 2:
            return 55
        elif total_articles >= 1:
            return 40
        else:
            return 20
    
    def _normalize_sentiment_ratio(self, positive_count: int, negative_count: int) -> float:
        """Normalize positive/negative sentiment ratio to 0-100 scale"""
        total = positive_count + negative_count
        if total == 0:
            return 50  # Neutral when no sentiment data
        
        positive_ratio = positive_count / total
        
        if positive_ratio >= 0.8:
            return 100
        elif positive_ratio >= 0.6:
            return 80
        elif positive_ratio >= 0.4:
            return 60
        elif positive_ratio >= 0.2:
            return 40
        else:
            return 20
    
    def _normalize_sentiment_consistency(self, volatility: float) -> float:
        """Normalize sentiment consistency (lower volatility is better)"""
        if volatility <= 0.1:
            return 100  # Very consistent
        elif volatility <= 0.2:
            return 80   # Consistent
        elif volatility <= 0.3:
            return 60   # Moderately consistent
        elif volatility <= 0.5:
            return 40   # Inconsistent
        else:
            return 20   # Very inconsistent
    
    def normalize_value_to_range(
        self, 
        value: Union[int, float], 
        min_val: Union[int, float], 
        max_val: Union[int, float], 
        target_min: Union[int, float] = 0, 
        target_max: Union[int, float] = 100
    ) -> float:
        """
        Normalize a value from one range to another
        
        Args:
            value: Value to normalize
            min_val: Minimum value of original range
            max_val: Maximum value of original range
            target_min: Minimum value of target range
            target_max: Maximum value of target range
            
        Returns:
            Normalized value in target range
        """
        try:
            if max_val == min_val:
                return target_min
            
            # Clamp value to original range
            value = max(min_val, min(max_val, value))
            
            # Normalize to 0-1 range
            normalized = (value - min_val) / (max_val - min_val)
            
            # Scale to target range
            return target_min + normalized * (target_max - target_min)
            
        except Exception as e:
            print(f"Error normalizing value: {e}")
            return target_min
    
    def calculate_percentile_score(self, value: float, value_list: List[float]) -> float:
        """
        Calculate percentile score of a value within a list
        
        Args:
            value: Value to score
            value_list: List of values for comparison
            
        Returns:
            Percentile score (0-100)
        """
        try:
            if not value_list or value is None:
                return 50.0
            
            # Remove None values and sort
            clean_list = [v for v in value_list if v is not None]
            if not clean_list:
                return 50.0
            
            clean_list.sort()
            
            # Find position of value in sorted list
            position = sum(1 for v in clean_list if v <= value)
            percentile = (position / len(clean_list)) * 100
            
            return max(0, min(100, percentile))
            
        except Exception as e:
            print(f"Error calculating percentile: {e}")
            return 50.0
    
    def get_score_interpretation(self, score: float) -> Dict[str, str]:
        """
        Get human-readable interpretation of a score
        
        Args:
            score: Score between 0-100
            
        Returns:
            Dictionary with interpretation details
        """
        if score >= 85:
            return {
                'grade': 'A',
                'description': 'Excellent',
                'color': 'green',
                'recommendation': 'Strong Buy'
            }
        elif score >= 70:
            return {
                'grade': 'B',
                'description': 'Good',
                'color': 'lightgreen',
                'recommendation': 'Buy'
            }
        elif score >= 55:
            return {
                'grade': 'C',
                'description': 'Fair',
                'color': 'yellow',
                'recommendation': 'Hold'
            }
        elif score >= 40:
            return {
                'grade': 'D',
                'description': 'Poor',
                'color': 'orange',
                'recommendation': 'Consider Selling'
            }
        else:
            return {
                'grade': 'F',
                'description': 'Very Poor',
                'color': 'red',
                'recommendation': 'Sell'
            }
