from datetime import datetime
from snsUtils import getConversationIdsFromUser, getThreads
from snscrape.modules.twitter import (
    Photo as snsPhoto,
    Video as snsVideo,
    Gif as snsGif
)
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from config import DB_URL, LOOKBACK_TWEETS, LOOKBACK_HOURS
from sqlalchemy.dialects.postgresql import insert
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
    max_bitrate = -1  # gifs will have a bitrate of 0
    for variant in video.variants:
        if variant.contentType == "video/mp4" and variant.bitrate > max_bitrate:
            max_bitrate = variant.bitrate
            url = variant.url
    return url


def bulk_upsert(session: Session, db_objects: list[models.Author] | list[models.Thread] | list[models.Tweet] | list[models.Media]):
    for db_object in db_objects:
        statement = insert(db_object.__class__).values(db_object.as_dict())
        statement = statement.on_conflict_do_update(
            constraint=db_object.__table__.primary_key,
            set_=db_object.upsert_dict())
        session.execute(statement)
        session.commit()


if __name__ == "__main__":
    # Fetch save_bots from db
    save_bots = get_save_bots()
    all_db_objects = []

    for save_bot in save_bots:
        print(f"Retrieving conversation_ids from @{save_bot.username}...")
        conversation_ids = getConversationIdsFromUser(
            username=save_bot.username, max_lookback_tweets=LOOKBACK_TWEETS, max_lookback_hours=LOOKBACK_HOURS)
        print(f"Retrieving {len(conversation_ids)} threads...")
        threads = getThreads(conversation_ids)

        print(f"Threads Retrieved. Building DB objects...")
        threads_db: list[models.Thread] = []
        authors_db: list[models.Author] = []
        tweets_db: list[models.Tweet] = []
        media_db: list[models.Media] = []

        # deconstruct threads into db objects: threads, tweets, authors, medias
        for thread in threads:
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
                links = []
                if tweet.links:
                    for link in tweet.links:
                        links.append(link.text)
                        links.append(link.url)

                tweets_db.append(
                    models.Tweet(
                        id=tweet.id,
                        thread_id=thread.id,
                        content=tweet.renderedContent,
                        links=links,
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
                                id=url,
                                type=type,
                                url=url,
                                tweet_id=tweet.id
                            )
                        )

        with Session(engine) as session:
            # update save_bot progress
            if tweets_db:
                save_bot.latest_tweet = tweets_db[-1].id
                save_bot.updated_at = datetime.now()
                session.add(save_bot)
                # session.commit

        all_db_objects.extend(authors_db)
        all_db_objects.extend(threads_db)
        all_db_objects.extend(tweets_db)
        all_db_objects.extend(media_db)

    print(f"Saving {len(all_db_objects)} objects...")
    bulk_upsert(session, all_db_objects)
