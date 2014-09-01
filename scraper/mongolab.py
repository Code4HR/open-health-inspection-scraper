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

import config
from pymongo import MongoClient
from bson.objectid import ObjectId

def connect():
    c = config.load()
    client = MongoClient(c["db_uri"])
    return client[c["db_name"]]

def new_id():
    return ObjectId()
