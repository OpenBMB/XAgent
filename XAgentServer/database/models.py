from sqlalchemy import JSON, Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(32), unique=True, index=True)
    email = Column(String(255), unique=True)
    name = Column(String(255))
    token = Column(String(255))
    available = Column(Boolean, default=True)
    deleted = Column(Boolean, default=False)
    corporation = Column(Text)
    industry = Column(Text)
    position = Column(String(255))
    create_time = Column(String(255))
    update_time = Column(String(255))


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(String(255))
    user_id = Column(String(255))
    create_time = Column(String(255))
    update_time = Column(String(255))
    description = Column(String(255))
    agent = Column(String(255))
    mode = Column(String(255))
    recorder_root_dir = Column(Text)
    file_list = Column(JSON)
    status = Column(String(255))
    message = Column(Text)
    current_step = Column(String(255))
    is_deleted = Column(Boolean, default=False)


class Parameter(Base):
    __tablename__ = "interaction_parameters"

    id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(String(32), unique=True, index=True)
    parameter_id = Column(String(32))
    args = Column(JSON)


class SharedInteraction(Base):
    __tablename__ = "shared_interactions"

    id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(String(255))
    user_name = Column(String(255))
    create_time = Column(String(255))
    update_time = Column(String(255))
    description = Column(String(255))
    agent = Column(String(255))
    mode = Column(String(255))
    is_deleted = Column(Boolean, default=False)
    star = Column(Integer, default=0)
    record_dir = Column(Text)
