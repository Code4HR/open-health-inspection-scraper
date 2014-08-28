import json
import os

ENV_DB_URI = 'SCRAPER_DB_URI'
ENV_DB_NAME = 'SCRAPER_DB_NAME'
ENV_SS_ID = 'SCRAPER_SS_ID'
ENV_SS_TOKEN = 'SCRAPER_SS_TOKEN'
ENV_STATE = 'SCRAPER_STATE'
ENV_STATE_ABB = 'SCRAPER_STATE_ABB'
ENV_VARIABLES = [
  ENV_DB_URI,
  ENV_DB_NAME,
  ENV_SS_ID,
  ENV_SS_TOKEN,
  ENV_STATE,
  ENV_STATE_ABB
]

def uses_env_vars():
    return reduce(lambda i,j: i and j,
        map(lambda k: os.environ.get(k) != None, ENV_VARIABLES))

def env_config():
    return {
        'db_uri': os.environ[ENV_DB_URI],
        'db_name': os.environ[ENV_DB_NAME],
        'ss_id': os.environ[ENV_SS_ID],
        'ss_token': os.environ[ENV_SS_TOKEN],
        'state': os.environ[ENV_STATE],
        'state_abb': os.environ[ENV_STATE_ABB]
    }

def load():
    if uses_env_vars():
        return env_config()
    else:
        with open('config.json','r') as f:
            return json.loads(f.read())
