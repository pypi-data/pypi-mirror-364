from deckgen.reader.base import BaseReader
from deckgen.reader.validations import validate_txt_file
from pathlib import Path


class FileReader(BaseReader):
    """
    A reader that reads content from a file.
    For now, it reads the entire content of the file into memory.
    This is suitable for small files. For larger files, consider implementing a streaming approach.
    It allows only reading text files with a .txt extension.
    """

    def __init__(self, file_path: str):
        """
        Initializes the FileReader with the provided file path.

        :param file_path: The path to the file to be read.
        """
        self.file_path = file_path if isinstance(file_path, Path) else Path(file_path)
        self.file_extension = self.file_path.suffix
        self.content = None

    def read(self):
        """
        Reads content from the specified file.

        :return: The content read from the file.
        :raises ValueError: If the file extension is not .txt.
        :raises FileNotFoundError: If the file does not exist.
        """
        validate_txt_file(self.file_path)
        with open(self.file_path, "r", encoding="utf-8") as file:
            self.content = file.read()
        return self.content

    def get_content(self):
        """
        Returns the content read from the file.

        :return: The content read from the file.
        """
        if self.content is None:
            self.read()
        return self.content
