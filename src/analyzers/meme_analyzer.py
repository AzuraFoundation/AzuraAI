from typing import Dict, Any, List, Optional
import hashlib
import json
from datetime import datetime
from database import Database
from dataclasses import dataclass
import aiohttp
from src.scrapers.reddit_scraper import RedditScraper
from src.scrapers.twitter_scraper import TwitterScraper

@dataclass
class MemeAnalysis:
    image_url: str
    popularity_score: float
    sentiment: str
    platform_origin: str
    related_coins: List[str]
    viral_potential: float

class MemeAnalyzer:
    def __init__(self, db: Database):
        self.db = db
        self.reddit_scraper = RedditScraper()
        self.twitter_scraper = TwitterScraper()

    async def analyze_meme(self, content: Dict[Any, Any]) -> Dict[str, Any]:
        """
        Analyzes meme content and stores results with hash
        
        Args:
            content: Dict containing meme data (text, image_url, source, etc.)
        Returns:
            Dict with analysis results and metadata
        """
        # Generate unique hash for the content
        content_hash = self._generate_hash(content)
        
        # Check if we already analyzed this content
        cached_result = self.db.get_analysis(content_hash)
        if cached_result:
            return cached_result

        # Download image for analysis if needed
        if content.get('image_url'):
            image_data = await self._download_image(content['image_url'])
            content['image_data'] = image_data

        # Perform analysis
        analysis_result = {
            'hash': content_hash,
            'timestamp': datetime.utcnow().isoformat(),
            'virality_score': await self._calculate_virality(content),
            'sentiment': await self._analyze_sentiment(content),
            'trend_indicators': await self._get_trend_indicators(content),
            'raw_content': {k: v for k, v in content.items() if k != 'image_data'}  # Don't store binary data
        }

        # Store in database
        self.db.save_analysis(content_hash, analysis_result)
        
        return analysis_result

    async def _download_image(self, url: str) -> bytes:
        """Downloads image data from URL"""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.read()

    def _generate_hash(self, content: Dict[Any, Any]) -> str:
        """Creates unique hash for content to avoid duplicate analysis"""
        # Remove binary data from hash calculation
        hash_content = {k: v for k, v in content.items() if k != 'image_data'}
        content_str = json.dumps(hash_content, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()

    async def _calculate_virality(self, content: Dict[Any, Any]) -> float:
        """Calculate potential virality score"""
        score = 0.5  # Base score
        
        # If content is from Reddit, use Reddit metrics
        if content.get('source', '').startswith('reddit'):
            upvote_ratio = content.get('upvote_ratio', 0.5)
            num_comments = content.get('num_comments', 0)
            post_score = content.get('score', 0)
            
            # Adjust score based on Reddit metrics
            score += (upvote_ratio - 0.5) * 0.3  # Upvote ratio contribution
            score += min(num_comments / 1000, 0.3)  # Comments contribution
            score += min(post_score / 10000, 0.4)  # Score contribution
        
        # If content is from Twitter, use Twitter metrics
        elif content.get('source') == 'twitter':
            tweet_id = content.get('tweet_id')
            if tweet_id:
                viral_score = await self.twitter_scraper.get_viral_coefficient(tweet_id)
                score = viral_score
        
        return max(0.0, min(1.0, score))  # Ensure score is between 0 and 1

    async def _analyze_sentiment(self, content: Dict[Any, Any]) -> Dict[str, float]:
        """Analyze sentiment of meme content"""
        # TODO: Implement actual sentiment analysis
        # For now, return random values
        import random
        positive = random.uniform(0.3, 0.8)
        negative = random.uniform(0, 1 - positive)
        neutral = 1 - positive - negative
        return {
            'positive': positive,
            'negative': negative,
            'neutral': neutral
        }

    async def _get_trend_indicators(self, content: Dict[Any, Any]) -> Dict[str, Any]:
        """Identify trend indicators in the meme"""
        # TODO: Implement actual trend analysis
        return {
            'trending_topics': ['crypto', 'defi', 'memes'],
            'related_memes': [],
            'popularity_metrics': {'score': 0.65}
        }

    async def analyze_trending_memes(self) -> List[MemeAnalysis]:
        """Analyze current trending memes across platforms"""
        # TODO: Implement actual analysis
        # Placeholder return
        return [
            MemeAnalysis(
                image_url="https://example.com/meme1.jpg",
                popularity_score=0.85,
                sentiment="Bullish",
                platform_origin="Twitter",
                related_coins=["DOGE", "PEPE"],
                viral_potential=0.75
            )
        ]

    async def get_meme_sentiment(self, meme_url: str) -> str:
        """Analyze sentiment of a specific meme"""
        # TODO: Implement sentiment analysis
        return "Bullish" 