import os
from dotenv import load_dotenv

if not os.environ.get('WORKFLOW_FLAG'):
    load_dotenv()

DB_URL = os.environ.get('DB_URL')
TWTR_BEARER_TOKEN = os.environ.get('TWTR_BEARER_TOKEN')