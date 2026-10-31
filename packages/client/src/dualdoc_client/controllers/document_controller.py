'Управление одним документом: загрузка, сохранение, перевод, коммиты (п. 5.2 ТЗ).'

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QObject, Signal

from dualdoc_client.core.document_manager import DocumentManager


class DocumentController(QObject):

    document_loaded = Signal(object)   # dict документа
    document_saved = Signal(str)       # path
    paragraph_translated = Signal(str, str)  # para_id, text
    commit_created = Signal(str)       # message
    status_message = Signal(str)
    error_occurred = Signal(str)

    def __init__(
        self,
        document_manager: DocumentManager | None = None,
        user_id: str = "local-user",
        parent=None,
    ):
        super().__init__(parent)
        self._manager = document_manager or DocumentManager()
        self.user_id = user_id

        #Поля из ТЗ
        self.document: dict[str, Any] | None = None
        self.api_client = None   # позже ApiClient
        self.local_mt = None     # позже LocalMtEngine
        self._file_path: str | None = None

    #загрузка / сохранение

    def load_document(self, doc_id: str) -> None:
        'id-заглушка'
        path = str(doc_id).strip()
        if not path:
            self.error_occurred.emit("Пустой id/путь документа")
            return

        try:
            loaded = self._manager.load_from_dualtrans(path)
        except Exception as exc:  # noqa: BLE001 — каркас, пока менеджер TODO
            self.error_occurred.emit(f"Ошибка загрузки: {exc}")
            self.status_message.emit(f"load_document: менеджер ещё TODO ({path})")
            return

        if loaded is None:
            #load_from_dualtrans сейчас pass → None
            self.status_message.emit(
                f"Загрузка {path}: serializer ещё не готов (заглушка)"
            )
            return

        self.document = loaded
        self._file_path = path
        self.document_loaded.emit(self.document)
        self.status_message.emit(f"Документ загружен: {path}")

    def save_document(self) -> None:
        if self.document is None:
            self.error_occurred.emit("Нет документа для сохранения")
            return

        path = self._file_path or "untitled.dualtrans"
        self._apply_user_to_document()

        try:
            self._manager.save_to_dualtrans(self.document, path)
        except Exception as exc:  # noqa: BLE001
            self.error_occurred.emit(f"Ошибка сохранения: {exc}")
            self.status_message.emit(f"save_document: менеджер ещё TODO ({path})")
            return

        self.document_saved.emit(path)
        self.status_message.emit(f"Сохранено (заглушка manager): {path}")

    def create_new_document(
        self,
        name: str,
        source_lang: str = "en",
        target_lang: str = "ru",
        file_path: str | None = None,
    ) -> None:
        'создать документ через manager + user_id.'
        doc = self._manager.create_document(name, source_lang, target_lang)
        #Подставляем user id (вместо "0" из менеджера)
        if "metadata" in doc:
            meta = doc["metadata"]
            if "author" in meta:
                meta["author"] = self.user_id
            meta["original_author"] = self.user_id
        self.document = doc
        self._file_path = file_path
        self.document_loaded.emit(self.document)
        self.status_message.emit(f"Создан документ: {name}")

    #перевод / коммит / ИИ (заглушки)

    def translate_paragraph(self, para_id: str, text: str) -> None:
        'Позже: online → api_client, offline → local_mt.'
        para_id = str(para_id)
        text = text or ""

        if self.api_client is not None:
            #translated = self.api_client.post_translation(...)
            self.status_message.emit("translate: ApiClient ещё не подключён")
            return
        if self.local_mt is not None:
            #translated = self.local_mt.translate(...)
            self.status_message.emit("translate: LocalMtEngine ещё не подключён")
            return

        #Заглушка: «перевод» = тот же текст с пометкой
        fake = f"[MT] {text}" if text else ""
        self._set_paragraph_translation(para_id, fake, status="translated")
        self.paragraph_translated.emit(para_id, fake)
        self.status_message.emit(f"Перевод абзаца {para_id} (заглушка)")

    def create_commit(self, message: str) -> None:
        if self.document is None:
            self.error_occurred.emit("Нет документа для коммита")
            return

        message = (message or "update").strip()
        history = self.document.setdefault("version_history", [])
        history.append(
            {
                "commit_hash": f"local-{len(history) + 1}",
                "message": message,
                "author": self.user_id,
                "parent_hash": history[-1]["commit_hash"] if history else None,
                "changes": {},
            }
        )
        self.commit_created.emit(message)
        self.status_message.emit(f"Коммит (локально в памяти): {message}")

    def apply_ai_suggestion(self, para_id: str, text: str) -> None:
        para_id = str(para_id)
        self._set_paragraph_translation(para_id, text or "", status="edited")
        self.paragraph_translated.emit(para_id, text or "")
        self.status_message.emit(f"AI-правка абзаца {para_id} (заглушка)")

    #вспомогательное

    def _apply_user_to_document(self) -> None:
        if not self.document:
            return
        meta = self.document.setdefault("metadata", {})
        if "author" in meta:
            meta["author"] = self.user_id
        meta.setdefault("original_author", self.user_id)

    def _set_paragraph_translation(
        self, para_id: str, text: str, status: str = "translated"
    ) -> None:
        if self.document is None:
            return
        content = self.document.setdefault("content", {})
        translations = content.setdefault("translations", {})
        meta = self.document.get("metadata") or {}
        lang = meta.get("target_lang") or "ru"
        paragraphs = translations.setdefault(lang, [])

        for p in paragraphs:
            if str(p.get("paragraph_id")) == para_id:
                p["text"] = text
                p["status"] = status
                p["updated_by"] = self.user_id
                return

        paragraphs.append(
            {
                "paragraph_id": para_id,
                "text": text,
                "status": status,
                "updated_by": self.user_id,
            }
        )
