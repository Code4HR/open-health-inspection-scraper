#   Copyright 2014 Code for Hampton Roads contributors
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

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
