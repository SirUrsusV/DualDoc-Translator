import os

from .parser_docx import DocxParser
from .parser_txt import TxtParser


class SourceParser:
    def get_parser(self, file_path: str):
        extension = os.path.splitext(file_path)[-1].lower()
        
        if extension == ".txt":
            return TxtParser() # Возвращаем объект парсера TXT
        elif extension == ".docx":
            return DocxParser() # Возвращаем объект парсера DOCX
        else:
            raise ValueError(f"Формат '{extension}' не поддерживается.")