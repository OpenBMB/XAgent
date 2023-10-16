import os
import docker
import sqlite3

from typing import List, Dict, Optional, Union

from motor.motor_asyncio import AsyncIOMotorClient
from motor.core import AgnosticDatabase
from config import CONFIG,logger

DB_TYPE = 'sqlite3'

db:Union[sqlite3.Connection,AgnosticDatabase] = None

if os.getenv('DB_USERNAME') is not None:
    DB_TYPE = 'mongodb'
    db_url = f"mongodb://{os.getenv('DB_USERNAME','')}:{os.getenv('DB_PASSWORD','')}@{os.getenv('DB_HOST','localhost')}:{os.getenv('DB_PORT','27017')}/"
    mongo_client = AsyncIOMotorClient(db_url)
    db:AgnosticDatabase = mongo_client[os.getenv('DB_COLLECTION','TSM')]
else:
    os.makedirs(os.path.split(CONFIG['database']['sqlite_db'])[0],exist_ok=True)
    db = sqlite3.connect(CONFIG['database']['sqlite_db'])
    
logger.info("Database connected")

docker_client = docker.from_env()
logger.info("Docker client connected")