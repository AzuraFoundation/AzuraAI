from typing import Dict, Any, List, Optional
import hashlib
import json
from datetime import datetime
from database import Database
from dataclasses import dataclass
import aiohttp
from src.scrapers.reddit_scraper import RedditScraper
from src.scrapers.twitter_scraper import TwitterScraper
from src.scrapers.telegram_scraper import TelegramScraper
from src.analyzers.content_analyzer import ContentAnalyzer
import asyncio
import re

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
        self.telegram_scraper = TelegramScraper()
        self.content_analyzer = ContentAnalyzer()

    async def start(self):
        """Initialize scrapers"""
        await self.telegram_scraper.start()

    async def stop(self):
        """Cleanup scrapers"""
        await self.telegram_scraper.stop()

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
            'sentiment': await self.content_analyzer.analyze_text_sentiment(
                content.get('text', '') or content.get('caption', '')
            ),
            'image_analysis': await self.content_analyzer.analyze_image_content(
                content.get('image_data', b'')
            ),
            'trend_indicators': await self.content_analyzer.analyze_trends(content),
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
        
        # If content is from Telegram, use Telegram metrics
        elif content.get('source') == 'telegram':
            message_id = content.get('message_id')
            channel = content.get('channel')
            if message_id and channel:
                viral_score = await self.telegram_scraper.get_viral_coefficient(message_id, channel)
                score = viral_score
        
        return max(0.0, min(1.0, score))  # Ensure score is between 0 and 1

    async def analyze_trending_memes(self) -> List[MemeAnalysis]:
        """
        Analyze trending memes across all platforms (Reddit, Twitter, Telegram)
        Returns aggregated and analyzed results
        """
        all_memes = []
        
        try:
            # Fetch memes from all platforms concurrently
            tasks = [
                self.reddit_scraper.get_trending_memes(limit=10),
                self.twitter_scraper.get_trending_memes(limit=10),
                self.telegram_scraper.get_trending_memes(limit=10)
            ]
            
            platform_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results from each platform
            for platform_idx, memes in enumerate(platform_results):
                if isinstance(memes, Exception):
                    print(f"Error fetching from platform {platform_idx}: {str(memes)}")
                    continue
                    
                for meme in memes:
                    try:
                        # Download and analyze image
                        if meme.get('image_url'):
                            image_data = await self._download_image(meme['image_url'])
                            meme['image_data'] = image_data
                        
                        # Perform comprehensive analysis
                        analysis = await self.analyze_meme(meme)
                        
                        # Extract relevant coins from text and trends
                        related_coins = self._extract_related_coins(
                            analysis['trend_indicators'].get('trending_topics', []),
                            meme.get('text', ''),
                            meme.get('caption', '')
                        )
                        
                        # Determine overall sentiment
                        sentiment_scores = analysis['sentiment']
                        overall_sentiment = "Neutral"
                        if sentiment_scores['positive'] > 0.6:
                            overall_sentiment = "Bullish"
                        elif sentiment_scores['negative'] > 0.6:
                            overall_sentiment = "Bearish"
                        
                        # Create MemeAnalysis object
                        meme_analysis = MemeAnalysis(
                            image_url=meme['image_url'],
                            popularity_score=analysis['trend_indicators']['popularity_metrics'].get('engagement_rate', 0.0),
                            sentiment=overall_sentiment,
                            platform_origin=meme['source'],
                            related_coins=related_coins,
                            viral_potential=analysis['virality_score']
                        )
                        
                        all_memes.append(meme_analysis)
                        
                    except Exception as e:
                        print(f"Error analyzing meme: {str(e)}")
                        continue
            
            # Sort by viral potential and popularity
            all_memes.sort(key=lambda x: (x.viral_potential + x.popularity_score), reverse=True)
            
            # Return top 10 memes
            return all_memes[:10]
            
        except Exception as e:
            print(f"Error in trending memes analysis: {str(e)}")
            return []

    def _extract_related_coins(self, topics: List[str], *texts: str) -> List[str]:
        """Extract cryptocurrency mentions from text and topics"""
        # Common memecoin symbols and names
        memecoin_patterns = {
            'DOGE': r'\b(doge(?:coin)?)\b',
            'SHIB': r'\b(shib(?:a)?(?:inu)?)\b',
            'PEPE': r'\b(pepe)\b',
            'WOJAK': r'\b(wojak)\b',
            'FLOKI': r'\b(floki)\b',
            'BONK': r'\b(bonk)\b',
            'MEME': r'\b(meme(?:coin)?)\b'
        }
        
        found_coins = set()
        
        # Check topics
        for topic in topics:
            topic_lower = topic.lower()
            for coin, pattern in memecoin_patterns.items():
                if re.search(pattern, topic_lower, re.IGNORECASE):
                    found_coins.add(coin)
        
        # Check texts
        for text in texts:
            if not text:
                continue
            text_lower = text.lower()
            for coin, pattern in memecoin_patterns.items():
                if re.search(pattern, text_lower, re.IGNORECASE):
                    found_coins.add(coin)
        
        return list(found_coins)

    async def get_meme_sentiment(self, meme_url: str) -> str:
        """Analyze sentiment of a specific meme"""
        # TODO: Implement sentiment analysis
        return "Bullish" 