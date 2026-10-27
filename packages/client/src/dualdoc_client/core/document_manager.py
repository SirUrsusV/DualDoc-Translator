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


    def load_from_dualtrans(self, path):
        # TODO: Реализовать после создания класса DualtransSerializer.
        pass


    def save_to_dualtrans(self, document, path):
        # TODO: Реализовать после создания класса DualtransSerializer.
        pass



