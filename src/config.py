import os
from dotenv import load_dotenv

if not os.environ.get("WORKFLOW_FLAG"):
    load_dotenv()

DB_URL = os.environ.get("DB_URL", "")
LOOKBACK_HOURS = os.environ.get("LOOKBACK_HOURS", "")
if not LOOKBACK_HOURS:
    LOOKBACK_TWEETS = os.environ.get("LOOKBACK_TWEETS", 1)
TWTR_BEARER_TOKEN = os.environ.get("TWTR_BEARER_TOKEN")
