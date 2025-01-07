from typing import List, Dict, Any, Optional
import tweepy
import os
from datetime import datetime, timedelta
import asyncio
from collections import Counter

class TwitterScraper:
    def __init__(self):
        # Initialize Twitter API v2 client
        self.client = tweepy.Client(
            bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
            consumer_key=os.getenv('TWITTER_API_KEY'),
            consumer_secret=os.getenv('TWITTER_API_SECRET'),
            access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
            access_token_secret=os.getenv('TWITTER_ACCESS_SECRET'),
            wait_on_rate_limit=True
        )
        
        # Common memecoin-related hashtags
        self.meme_hashtags = [
            'memecoin', 'memecrypto', 'cryptomemes',
            'dogecoin', 'shibainu', 'pepe', 'wojak',
            'memeconomy', 'cryptoart', 'nftmemes'
        ]

    async def get_trending_memes(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Fetch trending meme-related tweets
        
        Args:
            limit: Maximum number of tweets to fetch
            
        Returns:
            List of tweet data dictionaries
        """
        try:
            # Create query from hashtags
            query = ' OR '.join([f'#{tag}' for tag in self.meme_hashtags])
            query += ' has:images -is:retweet'  # Only tweets with images, no retweets
            
            # Search tweets
            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=limit,
                tweet_fields=['created_at', 'public_metrics', 'entities'],
                expansions=['attachments.media_keys'],
                media_fields=['url', 'preview_image_url']
            )
            
            # Process tweets
            memes = []
            media_lookup = {m.media_key: m for m in tweets.includes['media']} if 'media' in tweets.includes else {}
            
            for tweet in tweets.data:
                # Get media URLs
                media_keys = tweet.data.get('attachments', {}).get('media_keys', [])
                media_urls = [media_lookup[key].url or media_lookup[key].preview_image_url 
                            for key in media_keys if key in media_lookup]
                
                if not media_urls:
                    continue
                
                # Extract metrics
                metrics = tweet.public_metrics
                
                meme_data = {
                    'tweet_id': tweet.id,
                    'text': tweet.text,
                    'image_urls': media_urls,
                    'source': 'twitter',
                    'timestamp': tweet.created_at.isoformat(),
                    'metrics': {
                        'likes': metrics['like_count'],
                        'retweets': metrics['retweet_count'],
                        'replies': metrics['reply_count'],
                        'quotes': metrics['quote_count']
                    },
                    'hashtags': [tag['tag'] for tag in tweet.entities.get('hashtags', [])]
                }
                
                memes.append(meme_data)
                
            return memes
            
        except Exception as e:
            print(f"Error fetching tweets: {str(e)}")
            return []

    async def get_memecoin_sentiment(self, coin: str, timeframe_hours: int = 24) -> Dict[str, Any]:
        """
        Analyze sentiment for a specific memecoin
        
        Args:
            coin: Coin symbol or name (e.g., 'doge', 'shib')
            timeframe_hours: Hours of data to analyze
            
        Returns:
            Dictionary containing sentiment metrics
        """
        try:
            # Create query for the coin
            query = f'#{coin} OR ${coin} -is:retweet'
            start_time = datetime.utcnow() - timedelta(hours=timeframe_hours)
            
            # Search tweets
            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=100,
                tweet_fields=['created_at', 'public_metrics'],
                start_time=start_time
            )
            
            if not tweets.data:
                return None
            
            # Calculate metrics
            total_tweets = len(tweets.data)
            total_likes = sum(tweet.public_metrics['like_count'] for tweet in tweets.data)
            total_retweets = sum(tweet.public_metrics['retweet_count'] for tweet in tweets.data)
            
            # Get common hashtags
            all_hashtags = []
            for tweet in tweets.data:
                if hasattr(tweet, 'entities') and 'hashtags' in tweet.entities:
                    all_hashtags.extend([tag['tag'].lower() for tag in tweet.entities['hashtags']])
            
            hashtag_counts = Counter(all_hashtags).most_common(5)
            
            return {
                'coin': coin,
                'timeframe_hours': timeframe_hours,
                'metrics': {
                    'total_tweets': total_tweets,
                    'total_likes': total_likes,
                    'total_retweets': total_retweets,
                    'avg_likes_per_tweet': total_likes / total_tweets if total_tweets > 0 else 0,
                    'avg_retweets_per_tweet': total_retweets / total_tweets if total_tweets > 0 else 0,
                    'tweets_per_hour': total_tweets / timeframe_hours
                },
                'trending_hashtags': dict(hashtag_counts),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"Error analyzing {coin} sentiment: {str(e)}")
            return None

    async def get_viral_coefficient(self, tweet_id: str) -> float:
        """
        Calculate viral coefficient for a tweet
        
        Args:
            tweet_id: ID of the tweet to analyze
            
        Returns:
            Viral coefficient score (0.0 to 1.0)
        """
        try:
            # Get tweet data
            tweet = self.client.get_tweet(
                tweet_id,
                tweet_fields=['created_at', 'public_metrics']
            )
            
            if not tweet.data:
                return 0.0
            
            metrics = tweet.data.public_metrics
            
            # Calculate time factor (newer tweets get higher weight)
            hours_ago = (datetime.utcnow() - tweet.data.created_at).total_seconds() / 3600
            time_factor = max(0.1, min(1.0, 24 / hours_ago if hours_ago > 0 else 1.0))
            
            # Calculate engagement rate
            total_engagement = (
                metrics['like_count'] + 
                metrics['retweet_count'] * 2 +  # Retweets weighted more
                metrics['reply_count'] * 1.5 +  # Replies weighted more than likes
                metrics['quote_count'] * 2      # Quotes weighted same as retweets
            )
            
            # Normalize to 0-1 range (assuming 10k is viral)
            engagement_score = min(1.0, total_engagement / 10000)
            
            # Combine factors
            return engagement_score * time_factor
            
        except Exception as e:
            print(f"Error calculating viral coefficient: {str(e)}")
            return 0.0 