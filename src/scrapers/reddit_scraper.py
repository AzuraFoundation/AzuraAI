from typing import List, Dict, Any
import asyncpraw
import os
from datetime import datetime

class RedditScraper:
    def __init__(self):
        self.reddit = asyncpraw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent='Azura AI Meme Analyzer v1.0'
        )
        
        # Popular meme subreddits
        self.meme_subreddits = [
            'cryptocurrencymemes',
            'dogecoin',
            'wallstreetbets',
            'SatoshiStreetBets',
            'CryptoMemes',
            'memecoin',
            'memeeconomy'
        ]

    async def get_trending_memes(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch trending memes from crypto-related subreddits
        
        Args:
            limit: Maximum number of memes to fetch per subreddit
            
        Returns:
            List of meme data dictionaries
        """
        memes = []
        
        for subreddit_name in self.meme_subreddits:
            try:
                subreddit = await self.reddit.subreddit(subreddit_name)
                
                # Get hot posts from subreddit
                async for submission in subreddit.hot(limit=limit):
                    # Check if post is an image
                    if submission.is_self or not any(submission.url.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                        continue
                        
                    meme_data = {
                        'title': submission.title,
                        'image_url': submission.url,
                        'source': f'reddit/r/{subreddit_name}',
                        'timestamp': datetime.fromtimestamp(submission.created_utc).isoformat(),
                        'score': submission.score,
                        'upvote_ratio': submission.upvote_ratio,
                        'num_comments': submission.num_comments,
                        'post_id': submission.id,
                        'metadata': {
                            'author': str(submission.author),
                            'permalink': f'https://reddit.com{submission.permalink}',
                            'is_original_content': submission.is_original,
                            'awards': len(submission.all_awardings) if hasattr(submission, 'all_awardings') else 0
                        }
                    }
                    
                    memes.append(meme_data)
                    
            except Exception as e:
                print(f"Error fetching from r/{subreddit_name}: {str(e)}")
                continue
                
        return memes

    async def get_subreddit_sentiment(self, subreddit_name: str, timeframe: str = 'day') -> Dict[str, Any]:
        """
        Analyze sentiment of a specific subreddit
        
        Args:
            subreddit_name: Name of the subreddit
            timeframe: Time period to analyze ('hour', 'day', 'week', 'month')
            
        Returns:
            Dictionary containing sentiment metrics
        """
        try:
            subreddit = await self.reddit.subreddit(subreddit_name)
            
            # Get posts from specified timeframe
            posts = []
            async for submission in subreddit.top(time_filter=timeframe, limit=100):
                posts.append({
                    'title': submission.title,
                    'score': submission.score,
                    'num_comments': submission.num_comments,
                    'upvote_ratio': submission.upvote_ratio
                })
            
            # Calculate basic metrics
            total_posts = len(posts)
            avg_score = sum(post['score'] for post in posts) / total_posts if total_posts > 0 else 0
            avg_comments = sum(post['num_comments'] for post in posts) / total_posts if total_posts > 0 else 0
            avg_ratio = sum(post['upvote_ratio'] for post in posts) / total_posts if total_posts > 0 else 0
            
            return {
                'subreddit': subreddit_name,
                'timeframe': timeframe,
                'metrics': {
                    'total_posts': total_posts,
                    'average_score': avg_score,
                    'average_comments': avg_comments,
                    'average_upvote_ratio': avg_ratio
                },
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"Error analyzing r/{subreddit_name}: {str(e)}")
            return None 