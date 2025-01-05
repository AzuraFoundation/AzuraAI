"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2025-01-04 14:21:20.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create meme_analyses table
    op.create_table('meme_analyses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('content_hash', sa.String(), nullable=True),
        sa.Column('image_url', sa.String(), nullable=True),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('virality_score', sa.Float(), nullable=True),
        sa.Column('sentiment_data', sqlite.JSON(), nullable=True),
        sa.Column('trend_indicators', sqlite.JSON(), nullable=True),
        sa.Column('raw_content', sqlite.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_meme_analyses_content_hash'), 'meme_analyses', ['content_hash'], unique=True)

    # Create reddit_posts table
    op.create_table('reddit_posts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('post_id', sa.String(), nullable=True),
        sa.Column('subreddit', sa.String(), nullable=True),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('score', sa.Integer(), nullable=True),
        sa.Column('upvote_ratio', sa.Float(), nullable=True),
        sa.Column('num_comments', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('metadata', sqlite.JSON(), nullable=True),
        sa.Column('analysis_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['analysis_id'], ['meme_analyses.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reddit_posts_post_id'), 'reddit_posts', ['post_id'], unique=True)

    # Create subreddit_metrics table
    op.create_table('subreddit_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('subreddit', sa.String(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('timeframe', sa.String(), nullable=True),
        sa.Column('total_posts', sa.Integer(), nullable=True),
        sa.Column('average_score', sa.Float(), nullable=True),
        sa.Column('average_comments', sa.Float(), nullable=True),
        sa.Column('average_upvote_ratio', sa.Float(), nullable=True),
        sa.Column('raw_metrics', sqlite.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('subreddit_metrics')
    op.drop_table('reddit_posts')
    op.drop_table('meme_analyses') 