'Управление одним документом: загрузка, сохранение, перевод, коммиты (п. 5.2 ТЗ).'

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from dualdoc_shared.serializer import DualtransSerializer
from PySide6.QtCore import QObject, Signal

from dualdoc_client.core.document_manager import DocumentManager
from dualdoc_client.core.parser.parser_source import SourceParser


def _build_default_manager() -> DocumentManager:
    return DocumentManager(
        parser=SourceParser(),
        serializer=DualtransSerializer(),
    )


class DocumentController(QObject):
    'Связка UI ↔ DocumentManager / Services. Реальный save/load через serializer.'

    document_loaded = Signal(object)
    document_saved = Signal(str)
    paragraph_translated = Signal(str, str)
    commit_created = Signal(str)
    status_message = Signal(str)
    error_occurred = Signal(str)

    def __init__(
        self,
        document_manager: DocumentManager | None = None,
        user_id: str = "local-user",
        parent=None,
    ):
        super().__init__(parent)
        self._manager = document_manager or _build_default_manager()
        self.user_id = user_id
        self.document: dict[str, Any] | None = None
        self.api_client = None
        self.local_mt = None
        self._file_path: str | None = None

    def load_document(self, doc_id: str) -> None:
        'doc_id на этом этапе — путь к .dualtrans.'
        path = str(doc_id).strip()
        if not path:
            self.error_occurred.emit("Пустой id/путь документа")
            return

        try:
            loaded = self._manager.load_from_dualtrans(path)
        except FileNotFoundError:
            self.error_occurred.emit(f"Файл не найден: {path}")
            return
        except Exception as exc:  # noqa: BLE001
            self.error_occurred.emit(f"Ошибка загрузки: {exc}")
            return

        if not loaded:
            self.error_occurred.emit(f"Пустой документ: {path}")
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
        self._touch_updated_at()

        try:
            self._manager.save_to_dualtrans(self.document, path)
        except Exception as exc:  # noqa: BLE001
            self.error_occurred.emit(f"Ошибка сохранения: {exc}")
            return

        self._file_path = path
        self.document_saved.emit(path)
        self.status_message.emit(f"Сохранено: {path}")

    def create_new_document(
        self,
        name: str,
        source_lang: str = "en",
        target_lang: str = "ru",
        file_path: str | None = None,
    ) -> None:
        try:
            doc = self._manager.create_document(
                name, source_lang, target_lang, self.user_id
            )
        except TypeError:
            #на случай старой сигнатуры без user_id
            doc = self._manager.create_document(name, source_lang, target_lang)
            meta = doc.setdefault("metadata", {})
            meta["original_author"] = self.user_id

        self.document = doc
        self._file_path = file_path
        self.document_loaded.emit(self.document)
        self.status_message.emit(f"Создан документ: {name}")

    def translate_paragraph(self, para_id: str, text: str) -> None:
        para_id = str(para_id)
        text = text or ""

        if self.api_client is not None:
            self.status_message.emit("translate: ApiClient ещё не подключён")
            return
        if self.local_mt is not None:
            self.status_message.emit("translate: LocalMtEngine ещё не подключён")
            return

        fake = f"[MT] {text}" if text else ""
        self._set_paragraph_translation(para_id, fake, status="translated")
        self.paragraph_translated.emit(para_id, fake)
        self.status_message.emit(f"Перевод абзаца {para_id} (заглушка MT)")

    def create_commit(self, message: str) -> None:
        if self.document is None:
            self.error_occurred.emit("Нет документа для коммита")
            return

        message = (message or "update").strip()
        history = self.document.setdefault("version_history", [])
        parent = history[-1]["commit_hash"] if history else None
        history.append(
            {
                "commit_hash": f"local-{len(history) + 1}",
                "message": message,
                "timestamp": datetime.now(UTC).strftime(
                    "%Y-%m-%dT%H:%M:%SZ"
                ),
                "author": self.user_id,
                "parent_hash": parent,
                "changes": {},
            }
        )
        self.commit_created.emit(message)
        self.status_message.emit(f"Коммит: {message}")

    def apply_ai_suggestion(self, para_id: str, text: str) -> None:
        para_id = str(para_id)
        self._set_paragraph_translation(para_id, text or "", status="edited")
        self.paragraph_translated.emit(para_id, text or "")
        self.status_message.emit(f"AI-правка абзаца {para_id}")

    def _touch_updated_at(self) -> None:
        if not self.document:
            return
        meta = self.document.setdefault("metadata", {})
        meta["updated_at"] = datetime.now(UTC).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
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
