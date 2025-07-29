from typing import List
from pathlib import Path


def validate_file_extension(file_path: str, allowed_extensions: List[str]):
    """
    Validates the file extension against a list of allowed extensions.

    :param file_path: The path to the file to be validated.
    :param allowed_extensions: A list of allowed file extensions.
    :raises ValueError: If the file extension is not in the allowed list.
    """
    if not any(file_path.suffix == ext for ext in allowed_extensions):
        raise ValueError(
            f"Invalid file type. Allowed types are: {', '.join(allowed_extensions)}"
        )


def validate_txt_file(file_path: str):
    """
    Validates the file extension to ensure it is a .txt file.

    :param file_path: The path to the file to be validated.
    :raises ValueError: If the file extension is not .txt.
    :raises FileNotFoundError: If the file does not exist.
    """

    validate_file_extension(file_path, [".txt"])
    # validate that the file exists
    if not Path(file_path).exists():
        raise FileNotFoundError(f"The file {file_path} does not exist.")
