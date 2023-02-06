from datetime import datetime
from snsUtils import getConversationIdsFromUser, getThread, Thread, getTweet, getThreads
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from config import DB_URL
import models

engine = create_engine(DB_URL)


def get_save_bots():
    """Retrieves save bot usernames from the savebot table"""
    save_bots = []

    with Session(engine) as session:
        save_bots = session.scalars(select(models.SaveBot)).all()
    return list(save_bots)


if __name__ == "__main__":
    # Fetch save_bots from db
    save_bot_usernames = get_save_bots()

    for save_bot in save_bot_usernames:
        conversation_ids = getConversationIdsFromUser(
            username=save_bot.username, max_lookback_tweets=1
        )
        threads = getThreads(conversation_ids)

        # deconstruct threads into db objects: threads, tweets, authors,
        for thread in threads:
            thread_db: models.Thread
            author_db: models.Author
            tweets_db: list[models.Tweet]

            first_tweet = thread.tweets[0]
            thread_db = models.Thread(
                id=first_tweet.id,
                author_id=first_tweet.user.id,
                like_count=first_tweet.likeCount,
                reply_count=first_tweet.replyCount,
                retweet_count=first_tweet.retweetCount,
                view_count=first_tweet.viewCount,
                lang=first_tweet.lang,
                tweeted_at=first_tweet.date,
                # sensitive=
                source_account_id=save_bot.id,
                length=len(thread.tweets),
                created_at=datetime.utcnow().replace(microsecond=0),
                updated_at=datetime.utcnow().replace(microsecond=0),
            )
            for tweet in thread.tweets:
                tweet_db: models.Tweet
                media_db: list[models.Media]

                if tweet.media:
                    for media in tweet.media:
                        media_db: models.Media
                        if media.__class__ == "snscrape.modules.twitter.Photo":
                            pass
                        elif media.__class__ == "snscrape.modules.twitter.Gid":
                            pass
                        elif media.__class__ == "snscrape.modules.twitter.Video":
                            pass
        # extract db objects from threads
