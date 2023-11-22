"""User CRUD"""
import abc

from sqlalchemy.orm import Session

from XAgentServer.database.interface.user import UserDBInterface
from XAgentServer.exts.exception_ext import XAgentDBError
from XAgentServer.models.user import XAgentUser


class UserCRUD(metaclass=abc.ABCMeta):
    """
    User CRUD
    """

    @classmethod
    def get_user_list(cls, db: Session) -> list[XAgentUser]:
        """
        get all users
        
        Args:
            db: database session
        """
        try:
            return UserDBInterface.get_user_list(db=db)
        except Exception as e:
            raise XAgentDBError(f"XAgent DB Error [User Module]: {str(e)}") from e

    @classmethod
    def get_user(cls,
                 db: Session,
                 user_id: str | None = None,
                 email: str | None = None) -> XAgentUser | None:
        """
        get user by user_id or email
        
        Args:
            db: database session
            user_id: user_id
            email: email
        
        Returns:
            user
        
        """
        try:
            return UserDBInterface.get_user(db=db, user_id=user_id, email=email)
        except Exception as e:
            raise XAgentDBError(f"XAgent DB Error [User Module]: {str(e)}") from e

    @classmethod
    def is_exist(cls,
                 db: Session,
                 user_id: str | None = None,
                 email: str | None = None):
        """
        check user is exist
        
        Args:
            db: database session
            user_id: user_id
            email: email
            
        Returns:
            bool

        """
        try:
            return UserDBInterface.is_exist(db=db, user_id=user_id, email=email)
        except Exception as e:
            raise XAgentDBError(f"XAgent DB Error [User Module]: {str(e)}") from e

    @classmethod
    def token_is_exist(cls,
                       db: Session,
                       user_id: str,
                       token: str | None = None):
        """
        check token is exist
        
        Args:
            db: database session
            user_id: user_id
            token: token
            
        Returns:
            bool

        """
        try:
            return UserDBInterface.token_is_exist(db=db, user_id=user_id, token=token)
        except Exception as e:
            raise XAgentDBError(f"XAgent DB Error [User Module]: {str(e)}") from e

    @classmethod
    def user_is_valid(cls, db: Session,
                      user_id: str | None = None,
                      email: str | None = None,
                      token: str | None = None):
        """
        check user is valid
        
        Args:
            db: database session
            user_id: user_id
            email: email
            token: token
            
        Returns:
            bool

        """
        try:
            return UserDBInterface.user_is_valid(db=db, user_id=user_id, email=email, token=token)
        except Exception as e:
            raise XAgentDBError(f"XAgent DB Error [User Module]: {str(e)}") from e

    @classmethod
    def add_user(cls, db: Session, user_dict: dict):
        """
        add user
        
        Args:
            db: database session
            user_dict: user dict
            
        Returns:
            None

        """
        try:
            UserDBInterface.add_user(db=db, user_dict=user_dict)
        except Exception as e:
            raise XAgentDBError(f"XAgent DB Error [User Module]: {str(e)}") from e

    @classmethod
    def update_user(cls, db: Session, user: XAgentUser):
        """
        update user
        
        Args:
            db: database session
            user: user
            
        Returns:
            None

        """
        try:
            UserDBInterface.update_user(db=db, user=user)
        except Exception as e:
            raise XAgentDBError(f"XAgent DB Error [User Module]: {str(e)}") from e
