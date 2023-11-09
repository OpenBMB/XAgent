from XAgentIO.output.base import BaseOutput


class HttpOutput(BaseOutput):
    """
    HttpOutput is a class for handling HTTP output. It inherits from the BaseOutput class.
    
    HTTP Output class helps us to handle all HTTP outputs by providing a standard way of processing.
    
    Attributes:
        None.
    
    """
    def __init__(self):
        """
        The Constructor for HttpOutput class.
        
        This method helps to initialize the object of HttpOutput class.
        
        Args:
            None.
            
        Returns:
            None.

        """
        super().__init__()

    def run(self, output):
        """
        This method prints output.
        
        This method accepts an output to be printed and is responsible for handling it.
        
        Args:
            output (str): The output to be printed.
        
        Returns:
            None.
        
        """
        print(output)