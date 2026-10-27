import ijson
import json
import os

class DualtransSerializer:
     """
    Отвечает за сериализацию (превращение в строку/файл) 
    и десериализацию (чтение) документов формата .dualtrans.
    """
    def serialize(self, document: dict)->str:
        """
        Превращает словарь Python в отформатированную строку JSON.
        ensure_ascii=False сохраняет кириллицу в читаемом виде,
        indent=4 делает файл красивым (с отступами).
        """
        return json.dumps(document, ensure_ascii=False, indent=4)

    def deserialize(self, document: str)->dict:
        """Превращает строку JSON обратно в словарь Python."""
        return json.loads(document)

    def save(self, document: dict, path)->bool:
        """
        Сохраняет документ в файл .dualtrans.
        Возвращает True символизируя успех операции.
        """
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.serialize(document))
        return True

    def load(self, path)->dict:
        """
        Загружает документ из файла.
        Использует гибридный подход: 
        -->для маленьких файлов (<15МБ) стандартный json,
        -->для больших — потоковый ijson (для экономии RAM).
        """
        document = {
          "version": None,
          "metadata":{}, 
          "content":{
            "source":[],
            "translations":{}
          },
          "version_history":[]
        }

        file_size = os.path.getsize(path)
        limit_size = 15 * 1024 * 1024 # Порог в 15 Мегабайт
        
        if file_size < limit_size:
            # Обычное чтение для небольших файлов
            with open(path, "r", encoding="utf-8") as f:
                return self.deserialize(f.read())
        else:
            # Потоковое чтение для больших файлов (через ijson)
            with open(path,"rb") as f:
                document["version"] = next(ijson.items(f, "version"))
            with open(path,"rb") as f:
                document["metadata"] = next(ijson.items(f, "metadata"))

            with open(path,"rb") as f:
                for paragraph in ijson.items(f, "content.source.item"):
                    document["content"]["source"].append(paragraph)

            with open(path,"rb") as f:
                for lang, item_lang in ijson.kvitems(f, "content.translations"):
                    document["content"]["translations"][lang] = item_lang
      
            with open(path, "rb") as f:
                for change in ijson.items(f, "version_history.item"):
                    document["version_history"].append(change)
            return document
