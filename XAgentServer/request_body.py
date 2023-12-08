import re
from typing import Optional, Union
from fastapi import Form
from pydantic import BaseModel, validator

class User(BaseModel):
    """
    A User model.

    Args:
    email (str): The email address of the user.
    token (Optional[str], optional): A token associated with the user. It may be None.

    Raises:
    ValueError: If the email address is empty or invalid.

    Attributes:
    email (str): The email address of the user.
    token (Optional[str], optional): A token associated with the user. It may be None.
    """

    email: str
    token: Optional[str] = None

    @validator("email")
    def email_is_valid(cls, v):
        """
        Validates the email address.

        Args:
        v (str): The email address to be validated.

        Returns:
        The valid email.

        Raises:
        ValueError: If ‘v’ is empty or invalid.
        """
        
        if v == "":
            raise ValueError("email is empty")
        if re.match(r"[^@]+@[^@]+\.[^@]+", v) == None:
            raise ValueError("email is invalid")
        
        return v



    # @validator("email")
    # def email_is_valid(cls, v):
    #     if v == "":
    #         raise ValueError("email is empty")
    #     if re.match(r"[^@]+@[^@]+\.[^@]+", v) == None:
    #         raise ValueError("email is invalid")
        
    #     return v


class RequestBody(BaseModel):
    """
    A model for the request body coming from an API request.

    Attributes:
    token (str): A unique string serving as the token of the request.
    query (str): A query string associated with the request.
    mode (str): Specifies the mode of the request.
    """

    token: str
    query: str
    mode: str