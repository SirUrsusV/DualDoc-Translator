'Работа с историей версий: коммиты, ветки, merge (п. 5.3 ТЗ).'

from __future__ import annotations

import copy
from typing import Any

from PySide6.QtCore import QObject, Signal


class VersionController(QObject):
    'UI-слой над version_history документа.'

    'Пока без отдельного VersionControl в core:'
    #- fetch_commits читает document["version_history"]
    #- rollback откатывает content, если в коммите есть snapshot
    #- merge_branches — заглушка до реализации веток в core

    commits_fetched = Signal(list)          # list[dict]
    rollback_done = Signal(str)             # commit_hash
    merge_done = Signal(str, str)           # source, target
    status_message = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, document: dict[str, Any] | None = None, parent=None):
        super().__init__(parent)
        self._document = document

    def set_document(self, document: dict[str, Any] | None) -> None:
        'Привязать текущий документ (из DocumentController.document).'
        self._document = document

    def fetch_commits(self, doc_id: str | None = None) -> list[dict[str, Any]]:
        'Вернуть список коммитов. doc_id пока не используется (документ уже в памяти).'
        _ = doc_id
        if self._document is None:
            self.error_occurred.emit("Нет документа для истории версий")
            self.commits_fetched.emit([])
            return []

        history = list(self._document.get("version_history") or [])
        self.commits_fetched.emit(history)
        self.status_message.emit(f"Коммитов: {len(history)}")
        return history

    def merge_branches(self, source: str, target: str) -> None:
        'Слияние веток — заглушка (нет модели branches в dualtrans на этапе 1).'
        source = str(source).strip()
        target = str(target).strip()
        if not source or not target:
            self.error_occurred.emit("Нужны source и target ветки")
            return

        self.status_message.emit(
            f"merge_branches({source} → {target}): "
            "пока заглушка, ждём VersionControl в core"
        )
        # Когда появится core.VersionControl.merge — вызвать здесь
        self.merge_done.emit(source, target)

    def rollback_to_commit(self, commit_hash: str) -> None:
        'Откат content к snapshot коммита (если snapshot сохраняли).'
        commit_hash = str(commit_hash).strip()
        if self._document is None:
            self.error_occurred.emit("Нет документа для rollback")
            return
        if not commit_hash:
            self.error_occurred.emit("Пустой commit_hash")
            return

        history = self._document.get("version_history") or []
        index = next(
            (
                i
                for i, c in enumerate(history)
                if str(c.get("commit_hash")) == commit_hash
            ),
            None,
        )
        if index is None:
            self.error_occurred.emit(f"Коммит не найден: {commit_hash}")
            return

        commit = history[index]
        snapshot = commit.get("snapshot")
        if snapshot is None:
            self.error_occurred.emit(
                f"У коммита {commit_hash} нет snapshot — "
                'rollback content невозможен (только история)'
            )
            return

        # Восстанавливаем content и обрезаем историю после этого коммита
        self._document["content"] = copy.deepcopy(snapshot.get("content", {}))
        if (
            "metadata" in snapshot
            and "metadata" in self._document
            and "updated_at" in snapshot["metadata"]
        ):
            self._document["metadata"]["updated_at"] = snapshot["metadata"][
                "updated_at"
            ]
        self._document["version_history"] = history[: index + 1]

        self.rollback_done.emit(commit_hash)
        self.status_message.emit(f"Откат к коммиту {commit_hash}")

    def attach_snapshot_to_last_commit(self) -> None:
        'Вспомогательно: сохранить текущий content в последний коммит.'

        'Вызывать после DocumentController.create_commit, если нужен rollback.'

        if self._document is None:
            return
        history = self._document.get("version_history") or []
        if not history:
            self.status_message.emit("Нет коммитов для snapshot")
            return
        history[-1]["snapshot"] = {
            "content": copy.deepcopy(self._document.get("content") or {}),
            "metadata": {
                "updated_at": (self._document.get("metadata") or {}).get(
                    "updated_at"
                ),
            },
        }
        self.status_message.emit("Snapshot прикреплён к последнему коммиту")
