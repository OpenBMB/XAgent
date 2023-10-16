import os
import docker

from motor.motor_asyncio import AsyncIOMotorClient
from motor.core import AgnosticDatabase
from config import CONFIG,logger


db_url = f"mongodb://{os.getenv('DB_USERNAME','')}:{os.getenv('DB_PASSWORD','')}@{os.getenv('DB_HOST','localhost')}:{os.getenv('DB_PORT','27017')}/"
mongo_client = AsyncIOMotorClient(db_url)
db:AgnosticDatabase = mongo_client[os.getenv('DB_COLLECTION','TSM')]

logger.info("Database connected")

docker_client = docker.from_env()
logger.info("Docker client connected")