import os
import docker
import sqlite3

from typing import List, Dict, Optional, Union

from motor.motor_asyncio import AsyncIOMotorClient
from motor.core import AgnosticDatabase
from config import CONFIG, logger

DB_TYPE = 'sqlite3'

# Database connection object
# It may be of two types, either a SQLite Connection (sqlite3.Connection) or 
# an AsyncIO MongoDB Client (AgnosticDatabase), depending on the environment variables set.
db: Union[sqlite3.Connection, AgnosticDatabase] = None

# Check if DB_USERNAME environment variable is set.
# If it is set, that means we are using MongoDB, else SQLite.
if os.getenv('DB_USERNAME') is not None:
    DB_TYPE = 'mongodb'
    
    db_url = f"mongodb://{os.getenv('DB_USERNAME', '')}:{os.getenv('DB_PASSWORD', '')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '27017')}/"
    
    # Create an instance of AsyncIOMotorClient for asynchronous MongoDB operations.
    # It will be used to connect to the MongoDB database.
    mongo_client = AsyncIOMotorClient(db_url)
    
    db: AgnosticDatabase = mongo_client[os.getenv('DB_COLLECTION', 'TSM')]
else:
    # Create the directory in the path if it does not exist already.
    os.makedirs(os.path.split(CONFIG['database']['sqlite_db'])[0], exist_ok=True)
    
    # Connect to SQLite database as specified by config settings.
    db = sqlite3.connect(CONFIG['database']['sqlite_db'])

# Log confirmation message
logger.info("Database connected")

# Define a Docker client object
# It will be used for controlling Docker using python.
# by default it reads the environmental variables DOCKER_HOST, DOCKER_TLS_HOSTNAME, 
# DOCKER_API_VERSION, DOCKER_CERT_PATH, DOCKER_SSL_VERSION, DOCKER_TLS, DOCKER_TLS_VERIFY and DOCKER_TIMEOUT.
docker_client = docker.from_env()

# Log confirmation message
logger.info("Docker client connected")