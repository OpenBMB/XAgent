from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from XAgentServer.application.core.envs import XAgentServerEnv
import os

SQLALCHEMY_DATABASE_URL = os.getenv('MYSQL_DB_URL', XAgentServerEnv.DB.db_url)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, pool_size=10, max_overflow=2, pool_timeout=3600, pool_recycle=7200
)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# if database is not exist, create it
Base.metadata.create_all(bind=engine)