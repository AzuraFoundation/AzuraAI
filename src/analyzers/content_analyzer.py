from typing import Dict, Any, List, Tuple
import torch
from transformers import pipeline
from PIL import Image
import io
import numpy as np
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import tensorflow_hub as hub
import tensorflow as tf
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re
from collections import Counter

class ContentAnalyzer:
    def __init__(self):
        # Initialize NLTK
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('averaged_perceptron_tagger')
        
        # Initialize models
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.image_model = pipeline("image-classification", model="microsoft/resnet-50")
        
        # Load Universal Sentence Encoder
        self.text_encoder = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")
        
        # Common crypto and meme-related terms
        self.crypto_terms = {
            'bullish', 'bearish', 'moon', 'hodl', 'fud', 'dyor', 'btc', 'eth',
            'altcoin', 'defi', 'nft', 'blockchain', 'token', 'wallet', 'dex',
            'mining', 'staking', 'yield', 'apy', 'dao'
        }
        
        self.meme_terms = {
            'pepe', 'wojak', 'chad', 'doge', 'stonks', 'wen', 'lambo', 'ape',
            'moon', 'fomo', 'rekt', 'based', 'ngmi', 'wagmi', 'ser', 'gm'
        }

    async def analyze_text_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of text content"""
        # Get VADER sentiment
        vader_scores = self.sentiment_analyzer.polarity_scores(text)
        
        # Normalize scores to positive/negative/neutral
        total = sum(abs(score) for score in vader_scores.values())
        if total == 0:
            total = 1
            
        return {
            'positive': max(0, vader_scores['pos'] / total),
            'negative': max(0, vader_scores['neg'] / total),
            'neutral': max(0, vader_scores['neu'] / total)
        }

    async def analyze_image_content(self, image_data: bytes) -> Dict[str, Any]:
        """Analyze image content for meme classification"""
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Get image classification
            predictions = self.image_model(image)
            
            # Extract relevant features
            features = {
                'classifications': [
                    {'label': p['label'], 'confidence': p['score']}
                    for p in predictions[:3]  # Top 3 predictions
                ],
                'has_text': self._detect_text_in_image(image),
                'color_profile': self._analyze_color_profile(image)
            }
            
            return features
            
        except Exception as e:
            print(f"Error analyzing image: {str(e)}")
            return {}

    def _detect_text_in_image(self, image: Image) -> bool:
        """Simple text detection in image based on edge detection"""
        # Convert to grayscale
        gray = image.convert('L')
        # Use edge detection
        edges = gray.filter('FIND_EDGES')
        # Check if there are significant edges (potential text)
        return np.array(edges).std() > 30

    def _analyze_color_profile(self, image: Image) -> Dict[str, float]:
        """Analyze color distribution in image"""
        # Convert to RGB and get color histogram
        rgb_image = image.convert('RGB')
        colors = rgb_image.getcolors(rgb_image.size[0] * rgb_image.size[1])
        
        if not colors:
            return {}
            
        # Calculate color distribution
        total_pixels = sum(count for count, _ in colors)
        return {
            'brightness': np.array(rgb_image).mean() / 255,
            'contrast': np.array(rgb_image).std() / 255
        }

    async def analyze_trends(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content for trends and patterns"""
        trends = {
            'trending_topics': [],
            'related_memes': [],
            'crypto_relevance': 0.0,
            'meme_relevance': 0.0,
            'popularity_metrics': {}
        }
        
        # Extract text content
        text = content.get('text', '') or content.get('caption', '')
        
        if text:
            # Tokenize and clean text
            tokens = word_tokenize(text.lower())
            tokens = [t for t in tokens if t not in stopwords.words('english')]
            
            # Find crypto and meme terms
            crypto_matches = self.crypto_terms.intersection(tokens)
            meme_matches = self.meme_terms.intersection(tokens)
            
            # Calculate relevance scores
            trends['crypto_relevance'] = len(crypto_matches) / max(len(tokens), 1)
            trends['meme_relevance'] = len(meme_matches) / max(len(tokens), 1)
            
            # Extract trending topics
            topics = self._extract_topics(tokens)
            trends['trending_topics'] = topics
        
        # Add platform-specific metrics
        metrics = content.get('metrics', {})
        if metrics:
            trends['popularity_metrics'] = {
                'engagement_rate': self._calculate_engagement_rate(metrics),
                'virality_score': self._calculate_virality_score(metrics),
                'trend_velocity': self._calculate_trend_velocity(metrics)
            }
        
        return trends

    def _extract_topics(self, tokens: List[str]) -> List[str]:
        """Extract main topics from tokens"""
        # Get word frequencies
        word_freq = Counter(tokens)
        
        # Filter common words and get top topics
        topics = [
            word for word, freq in word_freq.most_common(5)
            if len(word) > 2 and not word.isnumeric()
        ]
        
        return topics

    def _calculate_engagement_rate(self, metrics: Dict[str, Any]) -> float:
        """Calculate engagement rate based on platform metrics"""
        total_engagement = sum(
            metrics.get(key, 0) for key in 
            ['likes', 'comments', 'shares', 'views', 'forwards', 'replies']
        )
        return min(1.0, total_engagement / 10000)  # Normalize to 0-1

    def _calculate_virality_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate virality score based on sharing metrics"""
        shares = sum(
            metrics.get(key, 0) for key in 
            ['shares', 'retweets', 'forwards']
        )
        return min(1.0, shares / 1000)  # Normalize to 0-1

    def _calculate_trend_velocity(self, metrics: Dict[str, Any]) -> float:
        """Calculate how quickly content is gaining traction"""
        # Use time-based metrics if available
        if 'created_at' in metrics:
            age_hours = (datetime.utcnow() - metrics['created_at']).total_seconds() / 3600
            engagement = self._calculate_engagement_rate(metrics)
            return min(1.0, engagement / max(age_hours, 1))
        return 0.0 