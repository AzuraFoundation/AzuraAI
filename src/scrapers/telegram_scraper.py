from typing import List, Dict, Any, Optional
from telethon import TelegramClient
from telethon.tl.types import Message, MessageMedia, Channel
from telethon.tl.functions.messages import GetHistoryRequest
import os
from datetime import datetime, timedelta
import asyncio
from collections import Counter

class TelegramScraper:
    def __init__(self):
        # Initialize Telegram client
        self.client = TelegramClient(
            'azura_scraper',
            api_id=os.getenv('TELEGRAM_API_ID'),
            api_hash=os.getenv('TELEGRAM_API_HASH')
        )
        
        # Popular meme and crypto channels
        self.target_channels = [
            'cryptomemesdaily',
            'wallstreetbets_memes',
            'defi_memes',
            'nftmemes',
            'wojak_memes',
            'memeconomy',
            'dogecoin_memes',
            'pepe_markets'
        ]

    async def start(self):
        """Start the Telegram client"""
        await self.client.start()

    async def stop(self):
        """Stop the Telegram client"""
        await self.client.disconnect()

    async def get_trending_memes(self, limit: int = 20, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Fetch trending memes from crypto/meme channels
        
        Args:
            limit: Maximum number of memes to fetch per channel
            hours: How many hours back to look
            
        Returns:
            List of meme data dictionaries
        """
        memes = []
        since_date = datetime.utcnow() - timedelta(hours=hours)
        
        for channel_username in self.target_channels:
            try:
                channel = await self.client.get_entity(channel_username)
                
                # Get messages from channel
                messages = await self.client.get_messages(
                    channel,
                    limit=limit,
                    offset_date=since_date,
                    filter=lambda m: m.media is not None  # Only messages with media
                )
                
                for message in messages:
                    if not message.media:
                        continue
                        
                    # Get media file
                    if hasattr(message.media, 'photo'):
                        media_obj = message.media.photo
                        media_type = 'photo'
                    elif hasattr(message.media, 'document') and message.media.document.mime_type.startswith('image/'):
                        media_obj = message.media.document
                        media_type = 'document'
                    else:
                        continue
                    
                    # Calculate engagement metrics
                    views = getattr(message, 'views', 0)
                    forwards = getattr(message, 'forwards', 0)
                    replies = getattr(message, 'replies', 0) if hasattr(message, 'replies') else 0
                    
                    meme_data = {
                        'message_id': message.id,
                        'channel': channel_username,
                        'text': message.text or message.caption or "",
                        'source': 'telegram',
                        'timestamp': message.date.isoformat(),
                        'media_type': media_type,
                        'metrics': {
                            'views': views,
                            'forwards': forwards,
                            'replies': replies
                        }
                    }
                    
                    memes.append(meme_data)
                    
            except Exception as e:
                print(f"Error fetching from {channel_username}: {str(e)}")
                continue
                
        return memes

    async def get_channel_stats(self, channel_username: str, days: int = 7) -> Dict[str, Any]:
        """
        Get channel statistics
        
        Args:
            channel_username: Channel username to analyze
            days: Number of days to analyze
            
        Returns:
            Dictionary containing channel metrics
        """
        try:
            channel = await self.client.get_entity(channel_username)
            since_date = datetime.utcnow() - timedelta(days=days)
            
            # Get messages
            messages = await self.client.get_messages(
                channel,
                limit=None,
                offset_date=since_date
            )
            
            # Calculate metrics
            total_messages = len(messages)
            media_messages = sum(1 for m in messages if m.media is not None)
            total_views = sum(getattr(m, 'views', 0) for m in messages)
            total_forwards = sum(getattr(m, 'forwards', 0) for m in messages)
            
            # Get common words/phrases
            text_content = ' '.join(m.text or m.caption or "" for m in messages if m.text or m.caption)
            words = text_content.lower().split()
            word_counts = Counter(words).most_common(10)
            
            return {
                'channel': channel_username,
                'timeframe_days': days,
                'metrics': {
                    'total_messages': total_messages,
                    'media_messages': media_messages,
                    'total_views': total_views,
                    'total_forwards': total_forwards,
                    'avg_views_per_post': total_views / total_messages if total_messages > 0 else 0,
                    'media_ratio': media_messages / total_messages if total_messages > 0 else 0
                },
                'trending_words': dict(word_counts),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"Error analyzing channel {channel_username}: {str(e)}")
            return None

    async def get_viral_coefficient(self, message_id: int, channel_username: str) -> float:
        """
        Calculate viral coefficient for a Telegram post
        
        Args:
            message_id: ID of the message to analyze
            channel_username: Channel where the message is from
            
        Returns:
            Viral coefficient score (0.0 to 1.0)
        """
        try:
            channel = await self.client.get_entity(channel_username)
            message = await self.client.get_messages(channel, ids=message_id)
            
            if not message:
                return 0.0
            
            # Calculate time factor
            hours_ago = (datetime.utcnow() - message.date).total_seconds() / 3600
            time_factor = max(0.1, min(1.0, 24 / hours_ago if hours_ago > 0 else 1.0))
            
            # Calculate engagement
            views = getattr(message, 'views', 0)
            forwards = getattr(message, 'forwards', 0)
            replies = getattr(message, 'replies', 0) if hasattr(message, 'replies') else 0
            
            # Weight different engagement types
            engagement_score = (
                views / 1000 +  # Base weight for views
                forwards * 5 +  # Forwards weighted heavily
                replies * 2     # Replies weighted moderately
            ) / 100  # Normalize to 0-1 range
            
            # Combine factors
            return min(1.0, engagement_score * time_factor)
            
        except Exception as e:
            print(f"Error calculating viral coefficient: {str(e)}")
            return 0.0 