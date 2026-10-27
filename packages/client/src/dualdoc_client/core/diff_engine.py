class DiffEngine:
    def compare(self, commit_old, commit_new):
        """
        Сравнивает два состояния документа и вычисляет разницу (дельту).
        
        Метод анализирует переводы на всех доступных языках и находит:
        добавленные, измененные и удаленные абзацы. 
        Изменения должны быть только в тексте. Остальное игнорируется.

        Аргументы:
            commit_old (dict): Словарь с предыдущим состоянием документа dualtrans(пока что JSON).
            commit_new (dict): Словарь с текущим состоянием документа dualtrans(пока что JSON).

        Возвращает:
            dict: Словарь с изменениями в формате(пример):
                  {
                      "changes": {
                          "ru": {
                                 "added": [{"id": "", text:""}, ...], 
                                 "modified": [{"id": "", text:""}, ...],
                                 "removed": [{"id": "", text:""}, ...]
                                  },
                           "de": {
                                 "added": [{"id": "", text:""}, ...], 
                                 "modified": [{"id": "", text:""}, ...],
                                 "removed": [{"id": "", text:""}, ...]
                                  },
                      }
                  }
        """
        changes_commit = {}
        
        # Формируем вложенные карты для быстрого поиска абзацев по ID
        # СТРУКТУРА ВЛОЖЕННЫХ КАРТ (map_old и map_new):
        # Мы используем словарь словарей для быстрого поиска абзаца по его ID (O(1)).
        # Выглядит это так:
        # {
        #     "ru": {                          <-- Язык (lang)
        #         "1": {                       <-- ID абзаца (section_id)
        #             "paragraph_id": "1",
        #             "text": "Какой-то текст",
        #             ...}
        #         },
        #         "2": { ... },
        #     },
        #     "de": { ... }
        # }
        map_old = {lang: {section["paragraph_id"]: section for section in item_lang} for lang, item_lang in commit_old["content"]["translations"].items()}
        map_new = {lang: {section["paragraph_id"]: section for section in item_lang} for lang, item_lang in commit_new["content"]["translations"].items()}
        
        # Объединяем множества языков, чтобы найти те, 
        # которые есть хотя бы в одном из коммитов
        all_langs = set(map_old.keys()) | set(map_new.keys())

        for lang_i in all_langs:             
            all_id = set(map_old.get(lang_i, {}).keys()) | set(map_new.get(lang_i, {}).keys())
            for section_id in all_id:
                
                # setdefault создает словарь для языка только при первом изменении
                lang_changes = changes_commit.setdefault(lang_i, {"added": [], "modified": [], "removed": []})

                # 1. Если абзаца не было раньше -> он добавлен
                if map_old.get(lang_i, {}).get(section_id) is None:
                    lang_changes["added"].append({"id":section_id, "text": map_new[lang_i][section_id]["text"]})

                # 2. Если абзаца нет сейчас -> он удален
                elif map_new.get(lang_i, {}).get(section_id) is None:
                    lang_changes["removed"].append({"id":section_id, "text": map_old[lang_i][section_id]["text"]})

                # 3. Если оба есть, но текст разный -> он изменен
                elif map_old.get(lang_i, {}).get(section_id, {}).get("text") != map_new.get(lang_i, {}).get(section_id, {}).get("text"):
                    lang_changes["modified"].append({"id":section_id, "text": map_new[lang_i][section_id]["text"]})
            
            # Очистка: если язык не имеет изменений, удаляем его 
            if changes_commit[lang_i] == {"added": [], "modified": [], "removed": []}:
                 del changes_commit[lang_i]
        return {"changes_commit": changes_commit}

