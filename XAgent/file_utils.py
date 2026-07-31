import os


def write_binary_file(directory: str, filename: str, data: bytes) -> str:
    """Write binary tool output, creating its local destination first."""
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)
    with open(path, "wb") as file:
        file.write(data)
    return path
