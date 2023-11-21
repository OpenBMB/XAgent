"""DB Interface: User"""
import abc
from datetime import datetime
import uuid

from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from XAgentServer.database.models import User
from XAgentServer.models.user import XAgentUser


class UserDBInterface(metaclass=abc.ABCMeta):
    """User DB Interface

    Args:
        UserBaseInterface (_type_): _description_
        metaclass (_type_, optional): _description_. Defaults to abc.ABCMeta.
    """

    @classmethod
    def get_user_list(cls, db: Session) -> list[XAgentUser]:
        """get all users

        Args:
            db (Session): db

        Returns:
            list[XAgentUser]: user list
        """
        users = db.query(User).all()
        return [XAgentUser.from_db(user) for user in users]

    @classmethod
    def get_user(cls,
                 db: Session,
                 user_id: str | None = None,
                 email: str | None = None) -> XAgentUser | None:
        """get user by user_id or email

        Args:
            db (Session): db
            user_id (str | None, optional): user id. Defaults to None.
            email (str | None, optional): email. Defaults to None.

        Returns:
            XAgentUser | None: user, if user is not exist, return None
        """
        if email is not None:
            user = db.query(User).filter(User.email == email,
                                         User.deleted.is_(False)).first()
        else:
            user = db.query(User).filter(
                User.user_id == user_id, User.deleted.is_(False)).first()

        return XAgentUser.from_db(user) if user else None

    @classmethod
    def is_exist(cls,
                db: Session,
                user_id: str | None = None,
                email: str | None = None):
        """user is exist?

        Args:
            db (Session): db session
            user_id (str | None, optional): user id. Defaults to None.
            email (str | None, optional): email. Defaults to None.

        Returns:
            Boolean: True or False
        """
        if not email and not user_id:
            return False
        if email:
            user = db.query(User).filter(User.email == email,
                                         User.deleted.is_(False)).first()
        else:
            user = db.query(User).filter(
                User.user_id == user_id, User.deleted.is_(False)).first()
        return user is not None

    @classmethod
    def token_is_exist(cls,
                       db: Session,
                       user_id: str,
                       token: str | None = None):
        """token is exist?
        
        Args:
            db (Session): db session
            user_id (str): user id
            token (str | None, optional): token. Defaults to None.
            
        Returns:
            Boolean: True or False
        """
        if not token:
            return False

        user = db.query(User).filter(User.user_id == user_id,
                                     User.token == token, User.deleted.is_(False)).first()
        return user is not None

    @classmethod
    def user_is_valid(cls, db: Session,
                      user_id: str | None = None,
                      email: str | None = None,
                      token: str | None = None):
        """
        user is valid?
        
        Args:
            db (Session): db session
            user_id (str | None, optional): user id. Defaults to None.
            email (str | None, optional): email. Defaults to None.
            token (str | None, optional): token. Defaults to None.
            
        Returns:
            Boolean: True or False
        """
        if email == "":
            return False
        user = db.query(User).filter(User.user_id == user_id,
                                     User.token == token, User.deleted.is_(False)).first()
        if user is None:
            return False
        if token is None:
            if user.email == email and user.available:
                return True
        if user_id is not None:
            if user.user_id == user_id and user.token == token and user.available:
                return True
        if email is not None:
            if user.email == email and user.token == token and user.available:
                return True
        return False

    @classmethod
    def add_user(cls, db: Session, user_dict: dict):
        """
        add user
        """
        db.add(User(**user_dict))
        db.commit()

    @classmethod
    def update_user(cls, db: Session, user: XAgentUser):
        """
        update user
        """
        db_user = db.query(User).filter(
            User.user_id == user.user_id, User.deleted.is_(False)).first()

        db_user.available = user.available
        db_user.email = user.email
        db_user.name = user.name
        db_user.token = user.token
        db_user.update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.commit()
