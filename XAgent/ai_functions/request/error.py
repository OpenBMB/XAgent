class FunctionCallSchemaError(Exception):
    """Exception raised when there is an error in the structure or format of a function call.

    This exception does not accept any arguments or custom messages. It is thrown when there is an issue
    with the schema or structure of a function call, such as passing the wrong data type, too many or too few
    arguments, etc. This error is used to halt execution and signal that the function call needs to be 
    corrected before the program can continue.
    """
    pass