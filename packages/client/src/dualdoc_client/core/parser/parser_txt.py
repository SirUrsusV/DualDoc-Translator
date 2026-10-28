from .parser_base import BaseParser


class TxtParser(BaseParser):
    def parse(self, file_path: str)->list:
        
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
        sections = text.split("\n\n")
        paragraphs = []
        for section_i in sections:
            clean_section_i = section_i.strip()
            if clean_section_i:
                paragraphs.append(clean_section_i)
        return paragraphs