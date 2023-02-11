import os
from dotenv import load_dotenv

if not os.environ.get("WORKFLOW_FLAG"):
    load_dotenv()

DB_URL = os.environ.get("DB_URL", "")

LOOKBACK_HOURS = int(os.environ.get("LOOKBACK_HOURS", 0))
LOOKBACK_TWEETS = int(os.environ.get("LOOKBACK_TWEETS", 0))

if not (LOOKBACK_HOURS or LOOKBACK_TWEETS):
    print("Error: Must set lookback hours or tweets.")
    quit()

TWTR_BEARER_TOKEN = os.environ.get("TWTR_BEARER_TOKEN")
