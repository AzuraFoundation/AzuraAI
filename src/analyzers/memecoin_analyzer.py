from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np
from dataclasses import dataclass

@dataclass
class MemecoinAnalysis:
    symbol: str
    sentiment_score: float  # -1 to 1
    virality_score: float  # 0 to 1
    trend_strength: float  # 0 to 1
    volume_prediction: float  # predicted volume change %
    price_impact: float  # predicted price impact %
    confidence: float  # 0 to 1
    supporting_data: Dict[str, Any]
    timestamp: str

class MemecoinAnalyzer:
    def __init__(self):
        # Common memecoin symbols and variations
        self.memecoin_map = {
            'DOGE': ['doge', 'dogecoin', 'shibainu', 'shib'],
            'PEPE': ['pepe', 'pepecoin'],
            'WOJAK': ['wojak', 'wojakcoin'],
            'FLOKI': ['floki', 'flokiinu'],
            'BONK': ['bonk', 'bonkcoin'],
            'MEME': ['meme', 'memecoin']
        }
        
        # Sentiment weights for different platforms
        self.platform_weights = {
            'reddit': 0.4,
            'twitter': 0.3,
            'telegram': 0.3
        }

    async def analyze_coin(self, 
                          symbol: str, 
                          meme_data: List[Dict[str, Any]], 
                          timeframe_hours: int = 24) -> Optional[MemecoinAnalysis]:
        """
        Analyze a specific memecoin based on aggregated meme data
        
        Args:
            symbol: Coin symbol (e.g., 'DOGE')
            meme_data: List of meme analysis results
            timeframe_hours: Analysis timeframe in hours
            
        Returns:
            MemecoinAnalysis object or None if insufficient data
        """
        try:
            # Filter relevant memes
            relevant_memes = self._filter_relevant_memes(symbol, meme_data, timeframe_hours)
            
            if len(relevant_memes) < 3:  # Require minimum data points
                return None
            
            # Calculate base metrics
            sentiment_score = self._calculate_weighted_sentiment(relevant_memes)
            virality_score = self._calculate_virality_impact(relevant_memes)
            trend_strength = self._calculate_trend_strength(relevant_memes)
            
            # Calculate market impact predictions
            volume_impact = self._predict_volume_impact(
                sentiment_score, virality_score, trend_strength
            )
            
            price_impact = self._predict_price_impact(
                sentiment_score, virality_score, trend_strength
            )
            
            # Calculate confidence score
            confidence = self._calculate_confidence(
                relevant_memes, sentiment_score, virality_score
            )
            
            # Compile supporting data
            supporting_data = {
                'meme_count': len(relevant_memes),
                'platform_distribution': self._get_platform_distribution(relevant_memes),
                'sentiment_breakdown': self._get_sentiment_breakdown(relevant_memes),
                'viral_posts': self._get_top_viral_posts(relevant_memes),
                'trend_indicators': self._extract_trend_indicators(relevant_memes)
            }
            
            return MemecoinAnalysis(
                symbol=symbol,
                sentiment_score=sentiment_score,
                virality_score=virality_score,
                trend_strength=trend_strength,
                volume_prediction=volume_impact,
                price_impact=price_impact,
                confidence=confidence,
                supporting_data=supporting_data,
                timestamp=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            print(f"Error analyzing {symbol}: {str(e)}")
            return None

    def _filter_relevant_memes(self, 
                             symbol: str, 
                             meme_data: List[Dict[str, Any]], 
                             timeframe_hours: int) -> List[Dict[str, Any]]:
        """Filter memes relevant to the coin within timeframe"""
        cutoff_time = datetime.utcnow() - timedelta(hours=timeframe_hours)
        relevant_terms = set(self.memecoin_map.get(symbol, []) + [symbol.lower()])
        
        filtered_memes = []
        for meme in meme_data:
            # Check timestamp
            meme_time = datetime.fromisoformat(meme['timestamp'])
            if meme_time < cutoff_time:
                continue
                
            # Check relevance
            text_content = (
                meme.get('text', '').lower() + ' ' +
                meme.get('caption', '').lower() + ' ' +
                ' '.join(meme.get('trend_indicators', {}).get('trending_topics', []))
            )
            
            if any(term in text_content for term in relevant_terms):
                filtered_memes.append(meme)
                
        return filtered_memes

    def _calculate_weighted_sentiment(self, memes: List[Dict[str, Any]]) -> float:
        """Calculate weighted sentiment score across platforms"""
        platform_sentiments = defaultdict(list)
        
        for meme in memes:
            platform = meme.get('source', 'unknown')
            sentiment = meme.get('sentiment', {})
            if sentiment:
                score = (
                    sentiment.get('positive', 0) -
                    sentiment.get('negative', 0)
                )
                platform_sentiments[platform].append(score)
        
        weighted_score = 0.0
        total_weight = 0.0
        
        for platform, scores in platform_sentiments.items():
            weight = self.platform_weights.get(platform, 0.1)
            if scores:
                weighted_score += np.mean(scores) * weight
                total_weight += weight
        
        return weighted_score / total_weight if total_weight > 0 else 0.0

    def _calculate_virality_impact(self, memes: List[Dict[str, Any]]) -> float:
        """Calculate overall virality impact"""
        virality_scores = [
            meme.get('virality_score', 0) for meme in memes
        ]
        
        if not virality_scores:
            return 0.0
            
        # Weight recent scores more heavily
        weights = np.linspace(0.5, 1.0, len(virality_scores))
        return float(np.average(virality_scores, weights=weights))

    def _calculate_trend_strength(self, memes: List[Dict[str, Any]]) -> float:
        """Calculate trend strength based on engagement patterns"""
        engagement_rates = []
        
        for meme in memes:
            metrics = meme.get('metrics', {})
            total_engagement = sum(
                metrics.get(key, 0) for key in 
                ['likes', 'comments', 'shares', 'views', 'forwards']
            )
            engagement_rates.append(total_engagement)
        
        if not engagement_rates:
            return 0.0
            
        # Calculate trend strength based on engagement growth
        sorted_rates = sorted(engagement_rates)
        trend_velocity = (
            (sorted_rates[-1] - sorted_rates[0]) / 
            max(sorted_rates[0], 1)
        )
        
        return min(1.0, max(0.0, trend_velocity))

    def _predict_volume_impact(self, 
                             sentiment: float, 
                             virality: float, 
                             trend: float) -> float:
        """Predict potential trading volume impact"""
        # Combine factors with different weights
        impact = (
            sentiment * 0.3 +
            virality * 0.4 +
            trend * 0.3
        )
        
        # Convert to percentage change prediction
        return impact * 100  # Convert to percentage

    def _predict_price_impact(self, 
                            sentiment: float, 
                            virality: float, 
                            trend: float) -> float:
        """Predict potential price impact"""
        # More conservative than volume impact
        impact = (
            sentiment * 0.4 +
            virality * 0.3 +
            trend * 0.3
        ) * 0.7  # Dampening factor
        
        return impact * 100  # Convert to percentage

    def _calculate_confidence(self, 
                            memes: List[Dict[str, Any]], 
                            sentiment: float, 
                            virality: float) -> float:
        """Calculate confidence score for the analysis"""
        # Factors affecting confidence:
        # 1. Number of data points
        data_confidence = min(len(memes) / 10, 1.0)
        
        # 2. Sentiment consistency
        sentiment_std = np.std([
            meme.get('sentiment', {}).get('positive', 0) -
            meme.get('sentiment', {}).get('negative', 0)
            for meme in memes
        ])
        sentiment_confidence = 1.0 - min(sentiment_std, 1.0)
        
        # 3. Virality consistency
        virality_std = np.std([
            meme.get('virality_score', 0) for meme in memes
        ])
        virality_confidence = 1.0 - min(virality_std, 1.0)
        
        # Combine confidence scores
        return (
            data_confidence * 0.4 +
            sentiment_confidence * 0.3 +
            virality_confidence * 0.3
        )

    def _get_platform_distribution(self, memes: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get distribution of memes across platforms"""
        distribution = defaultdict(int)
        for meme in memes:
            distribution[meme.get('source', 'unknown')] += 1
        return dict(distribution)

    def _get_sentiment_breakdown(self, memes: List[Dict[str, Any]]) -> Dict[str, float]:
        """Get detailed sentiment breakdown"""
        total_positive = 0
        total_negative = 0
        total_neutral = 0
        
        for meme in memes:
            sentiment = meme.get('sentiment', {})
            total_positive += sentiment.get('positive', 0)
            total_negative += sentiment.get('negative', 0)
            total_neutral += sentiment.get('neutral', 0)
            
        total = len(memes) or 1
        return {
            'positive': total_positive / total,
            'negative': total_negative / total,
            'neutral': total_neutral / total
        }

    def _get_top_viral_posts(self, memes: List[Dict[str, Any]], limit: int = 5) -> List[Dict[str, Any]]:
        """Get most viral posts"""
        sorted_memes = sorted(
            memes,
            key=lambda x: x.get('virality_score', 0),
            reverse=True
        )
        
        return [
            {
                'platform': meme.get('source'),
                'virality_score': meme.get('virality_score'),
                'url': meme.get('url'),
                'timestamp': meme.get('timestamp')
            }
            for meme in sorted_memes[:limit]
        ]

    def _extract_trend_indicators(self, memes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract trend indicators from meme data"""
        all_topics = []
        all_hashtags = []
        
        for meme in memes:
            trends = meme.get('trend_indicators', {})
            all_topics.extend(trends.get('trending_topics', []))
            all_hashtags.extend(trends.get('hashtags', []))
        
        return {
            'common_topics': self._get_frequency_list(all_topics),
            'common_hashtags': self._get_frequency_list(all_hashtags)
        }

    def _get_frequency_list(self, items: List[str], limit: int = 5) -> List[Tuple[str, int]]:
        """Get frequency list of items"""
        frequency = defaultdict(int)
        for item in items:
            frequency[item] += 1
        
        return sorted(
            frequency.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit] 