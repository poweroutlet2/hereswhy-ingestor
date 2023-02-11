# coding: utf-8
from sqlalchemy import create_engine
from sqlalchemy import BigInteger, Boolean, Column, Computed, DateTime, ForeignKey, Index, Integer, String, Table, Text, UniqueConstraint, ARRAY, text, UUID
from sqlalchemy.dialects.postgresql import TIMESTAMP, TSVECTOR
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata

engine = create_engine("sqlite://", echo=True)


class MixinDictHelpers:
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def upsert_dict(self):
        res = self.as_dict()
        res.pop('id')
        if res.get('created_at', None):
            res.pop('created_at')
        if res.get('source_account_id', None):
            res.pop('source_account_id')
        if res.get('search', None):
            res.pop('search')

        return res


class Author(MixinDictHelpers, Base):
    __tablename__ = 'author'

    id = Column(BigInteger, primary_key=True)
    username = Column(Text)
    display_name = Column(Text)
    follower_count = Column(Integer)
    following_count = Column(Integer)
    created_at = Column(DateTime, server_default=text("now()"))
    updated_at = Column(DateTime, server_default=text("now()"))
    source_account_id = Column(BigInteger)
    profile_picture_url = Column(Text)


class Category(MixinDictHelpers, Base):
    __tablename__ = 'category'

    id = Column(BigInteger, primary_key=True)
    title = Column(String(100), nullable=False, index=True)
    description = Column(String(255), index=True)


class SaveBot(MixinDictHelpers, Base):
    __tablename__ = 'save_bot'

    id = Column(BigInteger, primary_key=True)
    username = Column(Text)
    display_name = Column(Text)
    latest_tweet = Column(BigInteger)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class User(MixinDictHelpers, Base):
    __tablename__ = 'user'

    id = Column(Text, primary_key=True)
    name = Column(Text)
    email = Column(Text, unique=True)
    emailVerified = Column(TIMESTAMP(precision=3))
    image = Column(Text)


t_verification_token = Table(
    'verification_token', metadata,
    Column('identifier', Text, nullable=False),
    Column('token', Text, nullable=False, unique=True),
    Column('expires', TIMESTAMP(precision=3), nullable=False),
    Index('verification_token_identifier_token_key',
          'identifier', 'token', unique=True)
)


class Account(MixinDictHelpers, Base):
    __tablename__ = 'account'
    __table_args__ = (
        Index('account_provider_providerAccountId_key',
              'provider', 'providerAccountId', unique=True),
    )

    id = Column(Text, primary_key=True)
    userId = Column(ForeignKey('user.id', ondelete='CASCADE',
                    onupdate='CASCADE'), nullable=False)
    type = Column(Text, nullable=False)
    provider = Column(Text, nullable=False)
    providerAccountId = Column(Text, nullable=False)
    expires_at = Column(Integer)
    token_type = Column(Text)
    scope = Column(Text)
    id_token = Column(Text)
    session_state = Column(Text)
    oauth_token = Column(Text)
    oauth_token_secret = Column(Text)

    user = relationship('User')


class List(MixinDictHelpers, Base):
    __tablename__ = 'list'

    id = Column(Integer, primary_key=True, server_default=text(
        "nextval('list_id_seq'::regclass)"))
    user_id = Column(ForeignKey('user.id'), nullable=False, index=True)
    name = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    user = relationship('User')


class Thread(MixinDictHelpers, Base):
    __tablename__ = 'thread'

    id = Column(BigInteger, primary_key=True)
    author_id = Column(ForeignKey('author.id'), nullable=False, index=True)
    like_count = Column(Integer)
    retweet_count = Column(Integer)
    reply_count = Column(Integer)
    view_count = Column(Integer)
    sensitive = Column(Boolean)
    tweeted_at = Column(DateTime, index=True, server_default=text("now()"))
    created_at = Column(DateTime, server_default=text("now()"))
    updated_at = Column(DateTime, server_default=text("now()"))
    length = Column(Integer)
    source_account_id = Column(BigInteger)
    lang = Column(String(5), index=True)

    author = relationship('Author')


class SavedThread(MixinDictHelpers, Base):
    __tablename__ = 'saved_thread'
    __table_args__ = (
        UniqueConstraint('list_id', 'thread_id'),
    )

    id = Column(Integer, primary_key=True, server_default=text(
        "nextval('saved_thread_id_seq'::regclass)"))
    list_id = Column(ForeignKey('list.id'), nullable=False, index=True,
                     server_default=text("nextval('saved_thread_list_id_seq'::regclass)"))
    thread_id = Column(ForeignKey('thread.id'), nullable=False, index=True)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime, index=True,
                        server_default=text("CURRENT_TIMESTAMP"))

    list = relationship('List')
    thread = relationship('Thread')


class ThreadCategory(MixinDictHelpers, Base):
    __tablename__ = 'thread_categories'
    __table_args__ = (
        UniqueConstraint('thread_id', 'category_id'),
    )

    id = Column(Integer, primary_key=True, server_default=text(
        "nextval('thread_categories_id_seq'::regclass)"))
    thread_id = Column(ForeignKey('thread.id'), index=True)
    category_id = Column(BigInteger, index=True)
    category_title = Column(String(100))

    thread = relationship('Thread')


class Tweet(MixinDictHelpers, Base):
    __tablename__ = 'tweet'

    id = Column(BigInteger, primary_key=True)
    thread_id = Column(ForeignKey('thread.id'), index=True)
    content = Column(Text, index=True)
    index = Column(Integer)
    links = Column(ARRAY(Text))
    # search = Column(TSVECTOR, Computed(
    #     "to_tsvector('english'::regconfig, content)", persisted=True), index=True)

    thread = relationship('Thread')


class Media(MixinDictHelpers, Base):
    __tablename__ = 'media'

    id = Column(UUID, primary_key=True, server_default="uuid_generate_v4()")
    type = Column(Text, nullable=False)
    url = Column(Text, nullable=False)
    preview_image_url = Column(Text)
    tweet_id = Column(ForeignKey('tweet.id'), nullable=False, index=True)

    tweet = relationship('Tweet')
