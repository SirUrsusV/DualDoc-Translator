from docx import Document

from .parser_base import BaseParser


class DocxParser(BaseParser):
    def parse(self, file_path: str)->list:
        doc = Document(file_path)
        paragraphs = []
        for section_i in doc.paragraphs:
            clean_section_i = section_i.text.strip()
            if clean_section_i:
                paragraphs.append(clean_section_i)
        return paragraphs