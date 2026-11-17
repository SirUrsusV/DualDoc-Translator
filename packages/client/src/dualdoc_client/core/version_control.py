import hashlib

#from copy import deepcopy
from datetime import datetime


class VersionControl:
	"""
	Управление версиями документа.
	Позволяет создавать коммиты, получать историю и сливать ветки.
	"""

	def create_commit(self, document: dict, message: str, author: str, lang: str, changes: dict) -> dict:
		"""
		Создает и возвращает новый коммит, а также добавляет его в историю документа.
		
		Аргументы:
			document (dict): Текущее состояние документа.
			message (str): Сообщение коммита (что изменилось).
			author (str): ID автора коммита.
			lang (str): язык, для которого создается коммит(подумать над несколькимим языками в одном коммите)
			changes (dict): изменения от DiffEngine
			
		Возвращает:
			dict: Созданный объект коммита.
		"""
		history = document.get("version_history", {})
		
		# Определяем хэш родителя (предыдущего коммита).
		# Если история пуста, значит это первый коммит и родителя нет.
		lang_list = history.get(lang, [])
		parent_hash = (lang_list[-1] if lang_list else {}).get("commit_hash", None)
		
		# Форматируем время под стандарт
		timestamp = datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

		# Генерируем уникальный хэш коммита.
		# Берем время,родительский хэш сообщение и автора, кодируем в байты и прогоняем через SHA-1.
		#Обрезаем наращивание хеша длиной родительского, то есть допустимые 32(можно использовать другое число)
		identical_str = f"{parent_hash}{message}{datetime.now.isoformat()}{author}"
		commit_hash = hashlib.sha1(identical_str.encode()).hexdigest()[:( len(parent_hash) if parent_hash else 32)]

		
		# Собираем структуру коммита
		commit = {
			"commit_hash": commit_hash,
			"message": message,
			"timestamp": timestamp,
			"author": author,
			"parent_hash": parent_hash,
			"changes": changes
		}
	
		# Безопасно добавляем коммит в историю
		document.setdefault("version_history", {}).setdefault(lang, []).append(commit)
		return commit


	def get_history(self, document: dict, lang: str) -> list:
		"""
		Возвращает список коммитов документа.
		Если истории нет, возвращает пустой список.
		"""
		return document.get("version_history", {}).get(lang, [])

	'''
	def merge(self, branch1: dict, branch2: dict) -> dict:
		"""
		Сливает две ветки (два состояния документа).
		Изменения из branch2 применяются к branch1.
		
		ВНИМАНИЕ: Текущая реализация не использует "базовый коммит".

		Поэтому удаление абзацев может работать некорректно.
		"""

		history1 = self.get_history(branch1)
		history2 = self.get_history(branch2)

		# Объединяем списки коммитов
		history = list(history1 + history2)
		
		# Убираем дубликаты коммитов.
		# Используем словарь, где ключ - хэш коммита.
		map_history = {commit["commit_hash"]: commit for commit in history}
		history = list(map_history.values())
		
		# Сортируем объединенную историю по времени (от старых к новым)
		history_sort = sorted(history, key=lambda changes: changes["timestamp"])

		# Делаем глубокую копию branch1, чтобы не испортить исходный документ
		merged_doc = deepcopy(branch1)
		merged_doc["version_history"] = history_sort

		# Безопасно достаем переводы, используя .get(), чтобы избежать KeyError на пустых документах
		map_branch1 = {lang: {section["paragraph_id"]: section for section in item_lang} for lang, item_lang in branch1.get("content",{}).get("translations",{}).items()}
		map_branch2 = {lang: {section["paragraph_id"]: section for section in item_lang} for lang, item_lang in branch2.get("content",{}).get("translations",{}).items()}

		conflicts = []
		
		# Проходимся по всем языкам и абзацам из второй ветки
		for lang, item_lang in map_branch2.items():
			for paragraph_id, paragraph in item_lang.items():
				
				# Если такой язык есть в первой ветке
				if map_branch1.get(lang, False):
					
					# Если такой абзац уже есть в первой ветке
					if map_branch1[lang].get(paragraph_id, False):
						# Проверяем на конфликт: сравниваем ТОЛЬКО текст
						if map_branch1[lang][paragraph_id]["text"] != paragraph["text"]:
							conflicts.append({
							"paragraph_id":paragraph_id,
							"lang": lang,
							"branch1_text": map_branch1[lang][paragraph_id]["text"],
							"branch2_text": paragraph["text"]
							})# добавляем в список id абзаца с конфликтом
							continue
					
					# Если абзаца нет в первой ветке - значит его добавили во второй. Просто добавляем.
					else:
						merged_doc["content"]["translations"][lang].append(paragraph)
				
				# Если языка вообще нет в первой ветке - добавляем язык целиком
				else:
					merged_doc["content"]["translations"][lang] = list(item_lang.values())
		
		# Проходимся по первой ветке, чтобы найти то, чего нет во второй.
		
		# ВНИМАНИЕ: Без базового коммита мы не можем отличить "удалили" от "не добавили".
		
		# Этот цикл может удалить абзацы, которые были добавлены ТОЛЬКО в branch1.
		for lang, item_lang in map_branch1.items():
			if map_branch2.get(lang, False):
				new_paragraph = []

				# Оставляем только те абзацы, которые есть во второй ветке
				for paragraph in merged_doc["content"]["translations"][lang]:
				    if map_branch2[lang].get(paragraph["paragraph_id"], False):
				    	new_paragraph.append(paragraph)
				    	
				# Заменяем старый список на отфильтрованный
				merged_doc["content"]["translations"][lang] = new_paragraph
				
		return {
				"status": "conflict" if conflicts else "success",
				"document": merged_doc,
				"conflicts": conflicts
				}
	'''