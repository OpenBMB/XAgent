from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from XAgentServer.database.models import Base
from XAgentServer.envs import XAgentServerEnv


class DBConnection:
    """
    A database connection class that creates a session with SQLAlchemy.
    
    ...

    Attributes
    ----------
    db_session : Session
        a Session instance of SQLAlchemy.

    Methods
    -------
    __init__(self, envs: XAgentServerEnv) -> None:
       Initializes a new DBConnection instance.

    """

    def __init__(self, envs: XAgentServerEnv) -> None:
        """
        Initializes a new DBConnection instance checking whether the passed environment 
        uses an SQL database. If it is not an SQL database, a ValueError is raised. 

        Args:
            envs (XAgentServerEnv): 
                 An instance of the XAgentServerEnv class indicating the current environment.  

        Raises:
            ValueError: If the database specified in the environment is not an SQL type. 
        """
        
        if envs.DB.db_type == "file":
            raise ValueError("Require a sql database, such as sqlite, mysql, postgresql")
        
        SQLALCHEMY_DATABASE_URL = envs.DB.db_url
        
        engine = create_engine(
            SQLALCHEMY_DATABASE_URL, pool_size=10, max_overflow=2, pool_timeout=30, pool_recycle=-1
        )

        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        # An instance of the SessionLocal is created and assigned 
        # to the db_session attribute of the DBConnection instance.
        self.db_session = SessionLocal()