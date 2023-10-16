from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from XAgentServer.database.models import Base
from XAgentServer.envs import XAgentServerEnv


class DBConnection:
    def __init__(self, envs: XAgentServerEnv) -> None:
        if envs.DB.db_type == "file":
            raise ValueError("Require a sql database, such as sqlite, mysql, postgresql")
        
        SQLALCHEMY_DATABASE_URL = envs.DB.db_url

        
        engine = create_engine(
            SQLALCHEMY_DATABASE_URL, pool_size=30, max_overflow=10, pool_timeout=30, pool_recycle=-1
        )

        # Base.metadata.create_all(bind=engine)
        
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        self.db = SessionLocal()


    def get_db(self):
        return self.db
    
    def close_db(self):
        self.db.close()