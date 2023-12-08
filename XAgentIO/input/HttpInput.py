from XAgentIO.input.base import BaseInput

class HttpInput(BaseInput):
    """
    A class to represent an HTTP input, inherit from the BaseInput class.

    This class should be used as a base class and implements some basic functionality that all HTTP inputs will share.
    Derived classes should provide an implementation for the run method.

    Attributes:
    ----------- 
    None 

    Methods:
    -------
    run() Raises NotImplementedError
    """

    def __init__(self):
        """
        Constructs all the necessary attributes for the HttpInput object by calling super class's init method.
        """
        super().__init__()

    def run(self):
        """
        Triggers the HTTP input.

        It's only a placeholder for child classes to overwrite. Calling this method directly
        from an instance of this class will throw a NotImplementedError.

        Raises:
        --------
        NotImplementedError: If the method is not overwritten by a child class.
        """
        raise NotImplementedError