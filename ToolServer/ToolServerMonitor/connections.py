import os
import docker

from motor.motor_asyncio import AsyncIOMotorClient
from motor.core import AgnosticDatabase
from config import CONFIG,logger

# Constructs MongoDB URL using host's environment variables.
# Uses default MongoDB credentials if not provided through environment variables.
db_url = f"mongodb://{os.getenv('DB_USERNAME','')}:{os.getenv('DB_PASSWORD','')}@{os.getenv('DB_HOST','localhost')}:{os.getenv('DB_PORT','27017')}/"

# Creates an asynchronous MongoDB client using the constructed URL.
mongo_client = AsyncIOMotorClient(db_url)

# Defines database object by fetching specific collection from the MongoDB client instance.
# The collection is either fetched from a host's environment variable or defaults to 'TSM'.
db: AgnosticDatabase = mongo_client[os.getenv('DB_COLLECTION','TSM')]

# Logs message after successful database connection.
logger.info("Database connected")

# Creates a Docker client from environment variables 
docker_client = docker.from_env()

# Logs message after successful Docker client connection.
logger.info("Docker client connected")