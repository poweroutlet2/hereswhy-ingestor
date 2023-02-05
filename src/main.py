from snsUtils import (
    getConversationIdsFromUser,
    getThread,
    Thread,
    getTweet,
    getThreads
)
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# an Engine, which the Session will use for connection
# resources
engine = create_engine("postgresql://scott:tiger@localhost/")

# create session and add objects
with Session(engine) as session:
    pass

if __name__ == '__main__':
    # Fetch save_bots from db
    save_bot_usernames = ['readwise', 'threadunroll']

    for save_bot in save_bot_usernames:
        conversation_ids = getConversationIdsFromUser(
            username=save_bot, max_lookback_hours=2)
        threads = getThreads(conversation_ids)

        # extract db objects from threads
