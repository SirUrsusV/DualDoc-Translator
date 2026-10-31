import json
import os

import ijson


class DualtransSerializer:
    """
    Отвечает за сериализацию (превращение в строку/файл)
    и десериализацию (чтение) документов формата .dualtrans.
    """

    def serialize(self, document: dict) -> str:
        """
        Превращает словарь Python в отформатированную строку JSON.
        """
        return json.dumps(document, ensure_ascii=False, indent=4)

    def deserialize(self, data: str) -> dict:
        """Превращает строку JSON обратно в словарь Python."""
        return json.loads(data)

    def save(self, document: dict, path: str) -> bool:
        """Сохраняет документ в файл .dualtrans."""
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.serialize(document))
        return True

    def load(self, path: str) -> dict:
        """
        Загружает документ из файла.
        Использует гибридный подход: для маленьких файлов (<15МБ)
        стандартный json, а для больших — потоковый ijson.
        """
        document = {
            "version": None,
            "metadata": {},
            "content": {"source": [], "translations": {}},
            "version_history": [],
        }

        file_size = os.path.getsize(path)
        limit_size = 15 * 1024 * 1024

        if file_size < limit_size:
            with open(path, "r", encoding="utf-8") as f:
                return self.deserialize(f.read())
        else:
            with open(path, "rb") as f:
                document["version"] = next(ijson.items(f, "version"))
            with open(path, "rb") as f:
                document["metadata"] = next(ijson.items(f, "metadata"))

            with open(path, "rb") as f:
                for paragraph in ijson.items(f, "content.source.item"):
                    document["content"]["source"].append(paragraph)

            with open(path, "rb") as f:
                for lang, item_lang in ijson.kvitems(f, "content.translations"):
                    document["content"]["translations"][lang] = item_lang

            with open(path, "rb") as f:
                for change in ijson.items(f, "version_history.item"):
                    document["version_history"].append(change)
                    
            return document