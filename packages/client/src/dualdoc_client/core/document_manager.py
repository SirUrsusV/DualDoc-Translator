from datetime import datetime
from uuid import uuid4


class DocumentManager:
    """
    Управляет созданием, загрузкой, сохранением документа.
    Хранит состояние документа в памяти в виде словаря, 
    соответствующего схеме .dualtrans.
    """
    def __init__(self, parser, serializer):
        self.parser = parser
        self.serializer = serializer

    def create_document(self, name, source_lang, target_lang, user_id):
        """
        Создает новый пустой документ в памяти.

        Аргументы:
            name (str): Название документа.
            source_lang (str): Код исходного языка.
            target_lang (str): Код целевого языка.
            user_id (str): ID пользователя, создавшего документ

        Возвращает:
            dict: Словарь с инициализированной структурой документа.
        """

        document = {
            "version": "1.0",
            "metadata": {
            # Генерируем уникальный ID и приводим к строке для корректной записи в JSON
            "document_id": str(uuid4()),
            "name": name,
            "original_author": user_id,
            "source_lang": source_lang,
            "target_lang": target_lang,
            # Форматируем время под стандарт ISO 8601
            "created_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "updated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            # Временная заглушка
            "team_id": "0"
            },
            "content": {
              "source": [],
              # Инициализируем пустой список для целевого языка, выбранного пользователем
              "translations": { target_lang: [] }
            },
            "version_history": []
        }
        return document

    def import_from_file(self, file_path, name, source_lang, target_lang, user_id):
        """
        Вспомогательный метод: читает файл через парсер и сразу 
        собирает готовый документ.
        """
        # 1. Фабрика выбирает нужный парсер (TxtParser или DocxParser)
        actual_parser = self.parser.get_parser(file_path)
        raw_texts = actual_parser.parse(file_path) # Получаем список абзацев
        
        # 2. Создаем пустой каркас
        doc = self.create_document(name, source_lang, target_lang, user_id)
        
        # 3. Наполняем source текстом из файла
        for index, text in enumerate(raw_texts):
            doc["content"]["source"].append({
                "paragraph_id": str(index + 1), 
                "text": text
            })
            
        return doc

    def load_from_dualtrans(self, path):
        """
        Загружает документ из файла .dualtrans.
        """
        # Просто вызываем метод load у нашего сериализатора
        return self.serializer.load(path)

    def save_to_dualtrans(self, document, path):
        """
        Сохраняет документ в файл .dualtrans.
        """
        # Просто вызываем метод save у нашего сериализатора
        return self.serializer.save(document, path)



