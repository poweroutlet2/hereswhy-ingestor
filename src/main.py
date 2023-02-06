from datetime import datetime
from snsUtils import getConversationIdsFromUser, getThread, Thread, getTweet, getThreads
from snscrape.modules.twitter import (
    Photo as snsPhoto,
    Video as snsVideo,
    Gif as snsGif
)
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from config import DB_URL
import models

engine = create_engine(DB_URL)


def get_save_bots():
    """Retrieves save bot usernames from the savebot table
    """

    save_bots = []

    with Session(engine) as session:
        save_bots = session.scalars(select(models.SaveBot)).all()
    return list(save_bots)


def get_variant_video_url(video: snsVideo | snsGif) -> str:
    """Finds the highest bitrate mp4 video url from the given media
    """

    url = video.variants[-1]
    max_bitrate = 0
    for variant in video.variants:
        if variant.contentType == "video/mp4" and variant.bitrate > max_bitrate:
            max_bitrate = variant.bitrate
            url = variant.url
    return url


if __name__ == "__main__":
    # Fetch save_bots from db
    save_bot_usernames = get_save_bots()

    for save_bot in save_bot_usernames:
        print(f"Retrieving conversation_ids from @{save_bot.username}...")
        conversation_ids = getConversationIdsFromUser(
            username=save_bot.username, max_lookback_tweets=50
        )
        print(f"Retrieving {len(conversation_ids)} threads...")
        threads = getThreads(conversation_ids)

        print(f"Threads Retrieved. Building DB objects...")
        threads_db: list[models.Thread] = []
        authors_db: list[models.Author] = []
        tweets_db: list[models.Tweet] = []
        media_db: list[models.Media] = []

        # deconstruct threads into db objects: threads, tweets, authors, medias
        for thread in threads:
            tweets_db: list[models.Tweet] = []

            first_tweet = thread.tweets[0]
            # Build author
            authors_db.append(
                models.Author(
                    id=first_tweet.user.id,
                    username=first_tweet.user.username,
                    display_name=first_tweet.user.displayname,
                    follower_count=first_tweet.user.followersCount,
                    following_count=first_tweet.user.friendsCount,
                    source_account_id=save_bot.id,
                    profile_picture_url=first_tweet.user.profileImageUrl
                )
            )
            # Build thread
            threads_db.append(
                models.Thread(
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
                )
            )

            # Build tweets and media
            for i, tweet in enumerate(thread.tweets):
                tweets_db.append(
                    models.Tweet(
                        id=tweet.id,
                        thread_id=thread.id,
                        content=tweet.rawContent,
                        index=i,
                    )
                )

                if tweet.media:
                    for media in tweet.media:
                        id, type, url = "", "", ""

                        if isinstance(media, snsPhoto):
                            type = "photo"
                            url = media.fullUrl
                        elif isinstance(media, snsGif):
                            type = "gif"
                            url = get_variant_video_url(media)
                        elif isinstance(media, snsVideo):
                            type = "video"
                            url = get_variant_video_url(media)

                        media_db.append(
                            models.Media(
                                id=id,
                                type=type,
                                url=url,
                                tweet_id=tweet.id
                            )
                        )
