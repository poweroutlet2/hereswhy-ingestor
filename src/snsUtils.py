"""hereswhy.io utilities for the snscrape package
"""

import dataclasses
from typing import Optional
from datetime import datetime, timezone, timedelta
import snscrape.modules.twitter as snstwitter
from snscrape.modules.twitter import (
    TwitterTweetScraperMode,
    Tweet,
    User,
)


@dataclasses.dataclass
class Thread:
    id: int
    tweets: list[Tweet]


def getTweet(tweet_id: str) -> Tweet | None:
    for i, tweet in enumerate(
        snstwitter.TwitterTweetScraper(
            tweetId=tweet_id, mode=TwitterTweetScraperMode.SINGLE
        ).get_items()
    ):
        return tweet


def getConversationIdsFromUser(
    username: str,
    max_lookback_tweets: Optional[int] = None,
    max_lookback_hours: Optional[int] = None,
) -> list[int]:
    """Gets unique conversation ids from the specified user's latest tweets. Either lookback tweets or hours must be set.
    Args:
        username: user to fetch tweets from
        lookback_tweet: number of most recent tweets to look at
        lookback_hours: number of hours to lookback
    """

    if not max_lookback_tweets and not max_lookback_hours:
        raise Exception(
            "Error: You must specify a either a max lookback num_tweets or num_hours."
        )

    conversation_ids = set()
    for i, tweet in enumerate(snstwitter.TwitterUserScraper(user=username).get_items()):
        if ((max_lookback_tweets and i > max_lookback_tweets - 1) or
            (max_lookback_hours and
                tweet.date < (datetime.now(timezone.utc) - timedelta(hours=max_lookback_hours)))):
            break
        if (tweet.id != tweet.conversationId and tweet.inReplyToTweetId != tweet.conversationId):
            conversation_ids.add(tweet.conversationId)
    return list(conversation_ids)


def getThread(conversation_id: int | str, min_thread_length=3) -> Thread | None:
    """Retrieves all tweets in the thread with the specified conversation_id.

    A tweet is considered a part of the thread if the author of the tweet is the same as the author of the first tweet,
    and if the tweet is replying to the author of the first tweet.

    Returns:
            If there are enough tweets in the thread, returns a Thread object with tweets ordered by their position in the thread

    """
    tweets: list[Tweet] = []
    author = ""
    for i, tweet in enumerate(
        snstwitter.TwitterTweetScraper(
            tweetId=int(conversation_id), mode=TwitterTweetScraperMode.SCROLL
        ).get_items()
    ):
        # add tweets to thread
        if not author:
            # if author is not set, the tweet is first tweet in thread
            author = tweet.user.username
            lang = tweet.lang
            tweets.append(tweet)
        elif tweet.user.username == author and tweet.inReplyToUser.username == author:
            tweets.append(tweet)
        else:
            break
    if len(tweets) >= min_thread_length:
        return Thread(id=int(conversation_id), tweets=tweets)


def getThreads(conversation_ids: list[int], exclude_ids: set() = None) -> list[Thread]:
    threads = []
    for id in conversation_ids:
        if not exclude_ids or id not in exclude_ids:
            try:
                thread = getThread(id)
            except e:
                print(f"Error in snscrape for conversation_id={id}")
                print(e.traceback())
            if thread:
                threads.append(thread)
    return threads
