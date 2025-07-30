# models for the database schema using SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, ForeignKey, JSON, UniqueConstraint, Date, Float, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import declarative_base, relationship
from pgvector.sqlalchemy import Vector

Base = declarative_base()

class Platform(Base):
    __tablename__ = 'platform'
    platform_id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

class Author(Base):
    __tablename__ = 'author'
    author_id = Column(Integer, primary_key=True)
    platform_id = Column(Integer, ForeignKey('platform.platform_id'), nullable=False)
    username = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), default='now()')
    __table_args__ = (UniqueConstraint('platform_id', 'username', name='unique_platform_user'),)

class Post(Base):
    __tablename__ = 'post'
    post_id = Column(Integer, primary_key=True)
    platform_id = Column(Integer, ForeignKey('platform.platform_id'))
    author_id = Column(Integer, ForeignKey('author.author_id'))
    content = Column(Text)
    language = Column(String, nullable=True)
    language_confidence = Column(Float, nullable=True)  # optional, confidence score for language detection, from 0.0 to 1.0
    external_post_id = Column(String, nullable=False)
    translated_content = Column(Text, nullable=True)  # optional, if content is translated
    post_type = Column(String)
    parent_post_id = Column(Integer, ForeignKey('post.post_id'))
    timestamp = Column(TIMESTAMP(timezone=True))
    url = Column(String)
    
    source_id = Column(String, nullable=True)  # subreddit name, Steam app ID, Discord channel ID
    upvotes = Column(Integer)
    downvotes = Column(Integer)
    replies = Column(Integer)
    playtime_forever = Column(Integer)
    
    post_metadata = Column("metadata", JSONB, key="post_metadata", nullable=True)
    
    __table_args__ = (UniqueConstraint('platform_id', 'external_post_id', name='unique_external_post'),)

class Game(Base):
    __tablename__ = 'game'
    game_id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    studio = Column(String, nullable=True)
    release_date = Column(Date)
    game_metadata = Column("metadata", JSONB, key="game_metadata", nullable=True)

class GamePost(Base):
    __tablename__ = 'gamepost'
    game_id = Column(Integer, ForeignKey('game.game_id'), primary_key=True)
    post_id = Column(Integer, ForeignKey('post.post_id'), primary_key=True)

class Tag(Base):
    __tablename__ = 'tag'
    tag_id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

class PostTag(Base):
    __tablename__ = 'posttag'
    post_id = Column(Integer, ForeignKey('post.post_id'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tag.tag_id'), primary_key=True)

class Embedding(Base):
    __tablename__ = 'embedding'
    post_id =  Column(Integer, ForeignKey('post.post_id'))
    model = Column(String, nullable=False)  # e.g., 'openai/text-embedding-3-small' or 'ollama/nomic-embed-text'
    content = Column(Text, nullable=False)
    embedding = Column(Vector(), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default='now()')
    
    __table_args__ = (PrimaryKeyConstraint("post_id", "model", name="unique_post_embedding"),)

class Analysis(Base):
    __tablename__ = 'analysis'
    post_id = Column(Integer, ForeignKey('post.post_id'), primary_key=True)
    sentiment_label = Column(String)
    sentiment_score = Column(Float)
    priority_score = Column(Integer)
    notes = Column(Text)

class Alert(Base):
    __tablename__ = 'alert'
    alert_id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('post.post_id'))
    alert_type = Column(String, nullable=True)
    alert_severity = Column(Integer, nullable=True)  # 5 for critical, 4 for high, 3 for medium, 2 for low, 1 for informational
    triggered_at = Column(TIMESTAMP(timezone=True), default='now()')
    reviewed = Column(Boolean, default=False)
    note = Column(Text, nullable=True)
    
class UserPreferences(Base):
    __tablename__ = 'userpreferences'
    key = Column(String, primary_key=True)
    value = Column(String)
    updated_at = Column(TIMESTAMP(timezone=True), default='now()')



TABLE_REGISTRY = {
    "platform": Platform,
    "game": Game,
    "author": Author,
    "post": Post,
    "gamepost": GamePost,
    "tag": Tag,
    "posttag": PostTag,
    "embedding": Embedding,
    "analysis": Analysis,
    "alert": Alert,
    "userpreferences": UserPreferences
}