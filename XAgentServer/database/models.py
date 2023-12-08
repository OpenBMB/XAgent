from sqlalchemy import JSON, Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class User(Base):
    """
    This class defines the structure of the 'users' table in the database.
    It contains all attributes and methods related to a User object.

    Attributes:
        id (Integer): Holds the the identifier of the User. 
        user_id (String): Holds the unique user ID.
        email (String): Holds the user's email address.
        name (String): Holds the user's name.
        token (String): Holds the user's token.
        available (Boolean): Holds the availability status of the user.
        deleted (Boolean): Holds the deletion status of the user.
        corporation (Text): Holds the name of the company or corporation the user belongs to.
        industry (Text): Holds the industry the user operates in.
        position (String): Holds the position of the user at the corporation.
        create_time (String): Holds the creation time of the user.
        update_time (String): Holds the last update time of the user.
    """

    __tablename__="users"

    id=Column(Integer,primary_key=True,index=True)
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
    """
    Represents the structure of the 'interactions' table in the database, 
    and defines the attributes and behaviors of an Interaction object.
    
    Attributes:
        id (Integer): Holds the the unique identifier of the Interaction.
        interaction_id (String): Holds the interaction ID.
        user_id (String): Holds the user ID involved in the interaction.
        create_time (String): Holds the creation time of the interaction.
        update_time (String): Indicates when the interaction was last updated.
        description (String): Brief explanation of the interaction.
        agent (String): Agent's name involved in the interaction.
        mode (String): Modality of the interaction.
        recorder_root_dir (Text): Root directory for saving interaction records.
        file_list (JSON): List of files related to the interaction.
        status (String): Status of the interaction.
        message (Text): messages involved in the interaction.
        current_step (String): Step where the interaction is currently at.
        is_deleted (Boolean): Indicates if the interaction has been deleted.
    """    

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
    """
    This class represents the structure of the 'interaction_parameters' table in the database. 
    It defines the attributes and behaviors of a Parameter object.
    
    Attributes:
        id (Integer): Unique identifier of the Parameter.
        interaction_id (String): ID of the interaction to which the parameter belongs.
        parameter_id (String): ID of the parameter.
        args (JSON): Holds the parameter arguments.
    """    
    __tablename__ = "interaction_parameters"

    id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(String(32), unique=True, index=True)
    parameter_id = Column(String(32))
    args = Column(JSON)


class SharedInteraction(Base):
    """
    Represents the structure of the 'shared_interactions' table in the database. 
    Models the attributes and behaviors of a SharedInteraction object.
    
    Attributes:
        id (Integer): Unique identifier for the shared interaction.
        interaction_id (String): ID of the interaction being shared.
        user_name (String): Name of the user who shared the interaction.
        create_time (String): Creation time of the shared interaction.
        update_time (String): When the shared interaction was last updated.
        description (String): Short explanation about the shared interaction.
        agent (String): Agent involved in the shared interaction.
        mode (String): Mode of the shared interaction.
        is_deleted (Boolean): Indicates if the shared interaction has been deleted.
        star (Integer): Star rating given to the shared interaction. Default is 0.
        record_dir (Text): Directory where records for the shared interaction are held.
    """    

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