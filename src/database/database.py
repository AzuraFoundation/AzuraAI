from sqlalchemy import create_engine, Column, Integer, String, Float, JSON, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from datetime import datetime
from typing import Optional, Dict, Any, List
import json
import os
from alembic.config import Config
from alembic import command

Base = declarative_base()

class MemeAnalysis(Base):
    __tablename__ = 'meme_analyses'
    
    id = Column(Integer, primary_key=True)
    content_hash = Column(String, unique=True, index=True)
    image_url = Column(String)
    source = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    virality_score = Column(Float)
    sentiment_data = Column(JSON)
    trend_indicators = Column(JSON)
    raw_content = Column(JSON)
    
    # Relationships
    reddit_data = relationship("RedditPost", back_populates="analysis", uselist=False)

class RedditPost(Base):
    __tablename__ = 'reddit_posts'
    
    id = Column(Integer, primary_key=True)
    post_id = Column(String, unique=True, index=True)
    subreddit = Column(String)
    title = Column(String)
    score = Column(Integer)
    upvote_ratio = Column(Float)
    num_comments = Column(Integer)
    created_at = Column(DateTime)
    metadata = Column(JSON)
    
    # Foreign key to MemeAnalysis
    analysis_id = Column(Integer, ForeignKey('meme_analyses.id'))
    analysis = relationship("MemeAnalysis", back_populates="reddit_data")

class SubredditMetrics(Base):
    __tablename__ = 'subreddit_metrics'
    
    id = Column(Integer, primary_key=True)
    subreddit = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    timeframe = Column(String)
    total_posts = Column(Integer)
    average_score = Column(Float)
    average_comments = Column(Float)
    average_upvote_ratio = Column(Float)
    raw_metrics = Column(JSON)

class Database:
    def __init__(self):
        db_path = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///memes.db')
        self.engine = create_async_engine(db_path, echo=True)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def init_db(self):
        """Initialize database tables and run migrations"""
        # Run migrations
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")

    async def save_analysis(self, content_hash: str, analysis_data: Dict[str, Any]) -> None:
        """Save meme analysis results"""
        async with self.async_session() as session:
            analysis = MemeAnalysis(
                content_hash=content_hash,
                image_url=analysis_data['raw_content'].get('image_url'),
                source=analysis_data['raw_content'].get('source'),
                timestamp=datetime.fromisoformat(analysis_data['timestamp']),
                virality_score=analysis_data['virality_score'],
                sentiment_data=analysis_data['sentiment'],
                trend_indicators=analysis_data['trend_indicators'],
                raw_content=analysis_data['raw_content']
            )
            
            # If it's from Reddit, save Reddit-specific data
            if analysis_data['raw_content'].get('source', '').startswith('reddit'):
                reddit_data = analysis_data['raw_content']
                reddit_post = RedditPost(
                    post_id=reddit_data['post_id'],
                    subreddit=reddit_data['source'].split('/')[-1],
                    title=reddit_data['title'],
                    score=reddit_data['score'],
                    upvote_ratio=reddit_data['upvote_ratio'],
                    num_comments=reddit_data['num_comments'],
                    created_at=datetime.fromisoformat(reddit_data['timestamp']),
                    metadata=reddit_data['metadata'],
                    analysis=analysis
                )
                session.add(reddit_post)
            
            session.add(analysis)
            await session.commit()

    async def get_analysis(self, content_hash: str) -> Optional[Dict[str, Any]]:
        """Retrieve analysis results by content hash"""
        async with self.async_session() as session:
            result = await session.get(MemeAnalysis, content_hash)
            if result:
                return {
                    'hash': result.content_hash,
                    'timestamp': result.timestamp.isoformat(),
                    'virality_score': result.virality_score,
                    'sentiment': result.sentiment_data,
                    'trend_indicators': result.trend_indicators,
                    'raw_content': result.raw_content
                }
            return None

    async def save_subreddit_metrics(self, metrics_data: Dict[str, Any]) -> None:
        """Save subreddit metrics"""
        async with self.async_session() as session:
            metrics = SubredditMetrics(
                subreddit=metrics_data['subreddit'],
                timeframe=metrics_data['timeframe'],
                total_posts=metrics_data['metrics']['total_posts'],
                average_score=metrics_data['metrics']['average_score'],
                average_comments=metrics_data['metrics']['average_comments'],
                average_upvote_ratio=metrics_data['metrics']['average_upvote_ratio'],
                raw_metrics=metrics_data['metrics']
            )
            session.add(metrics)
            await session.commit()

    async def get_recent_analyses(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent meme analyses"""
        async with self.async_session() as session:
            query = session.query(MemeAnalysis)\
                .order_by(MemeAnalysis.timestamp.desc())\
                .limit(limit)
            results = await session.execute(query)
            return [
                {
                    'hash': result.content_hash,
                    'timestamp': result.timestamp.isoformat(),
                    'virality_score': result.virality_score,
                    'sentiment': result.sentiment_data,
                    'trend_indicators': result.trend_indicators,
                    'raw_content': result.raw_content
                }
                for result in results
            ] 