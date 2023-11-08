from XAgentIO.input.base import BaseInput


class RestApiInput(BaseInput):
    """A class used to represent RestApi input which inherits from `BaseInput`. 

    This class is a base class for all input classes that are intended
    to handle RestApi inputs.

    Note:
        Do not use this class directly, use one of its child classes instead.

    Attributes:
        None
    """

    def __init__(self):
        """Initializes `RestApiInput` instances by calling the __init__ method of the base class."""
        super().__init__()

    def run(self):
        """This function is meant to be overridden in child classes.

        Raises:
            NotImplementedError: Always, since it should be implemented in a child class.
        """
        raise NotImplementedError