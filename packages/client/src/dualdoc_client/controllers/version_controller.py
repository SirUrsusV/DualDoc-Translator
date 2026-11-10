'Работа с историей версий: коммиты, ветки, merge (п. 5.3 ТЗ)'

from __future__ import annotations

import copy
from typing import Any

from PySide6.QtCore import QObject, Signal


class VersionController(QObject):
    'UI-слой над version_history документа.'

    commits_fetched = Signal(list)
    rollback_done = Signal(str)
    merge_done = Signal(str, str)  # совместимость: source, target
    merge_finished = Signal(dict)  # полный результат слияния
    status_message = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, document: dict[str, Any] | None = None, parent=None):
        super().__init__(parent)
        self._document = document

    def set_document(self, document: dict[str, Any] | None) -> None:
        self._document = document

    def fetch_commits(self, doc_id: str | None = None) -> list[dict[str, Any]]:
        _ = doc_id
        if self._document is None:
            self.error_occurred.emit("Нет документа для истории версий")
            self.commits_fetched.emit([])
            return []

        history = list(self._document.get("version_history") or [])
        self.commits_fetched.emit(history)
        self.status_message.emit(f"Коммитов: {len(history)}")
        return history

    def merge_branches(self, source: str, target: str) -> dict[str, Any]:
        '''Слияние двух версий.
        source / target — commit_hash из version_history (пока нет модели веток).
        У обоих коммитов желателен snapshot.content.
        Возвращает:
          ok, status ('ok'|'conflicts'|'error'), message, conflicts[], merged_content
        '''
        source = str(source).strip()
        target = str(target).strip()

        if not source or not target:
            result = self._merge_result(
                ok=False,
                status="error",
                message="Нужны source и target (commit_hash)",
            )
            self._emit_merge(result, source, target)
            return result

        if self._document is None:
            result = self._merge_result(
                ok=False,
                status="error",
                message="Нет документа для merge",
            )
            self._emit_merge(result, source, target)
            return result

        if source == target:
            result = self._merge_result(
                ok=False,
                status="error",
                message="source и target совпадают",
            )
            self._emit_merge(result, source, target)
            return result

        src_commit = self._find_commit(source)
        tgt_commit = self._find_commit(target)

        if src_commit is None:
            result = self._merge_result(
                ok=False,
                status="error",
                message=f"Source-коммит не найден: {source}",
            )
            self._emit_merge(result, source, target)
            return result

        if tgt_commit is None:
            result = self._merge_result(
                ok=False,
                status="error",
                message=f"Target-коммит не найден: {target}",
            )
            self._emit_merge(result, source, target)
            return result

        src_snap = (src_commit.get("snapshot") or {}).get("content")
        tgt_snap = (tgt_commit.get("snapshot") or {}).get("content")

        if src_snap is None or tgt_snap is None:
            result = self._merge_result(
                ok=False,
                status="error",
                message=(
                    'У source или target нет snapshot — '
                    'сначала attach_snapshot_to_last_commit при коммитах'
                ),
            )
            self._emit_merge(result, source, target)
            return result

        conflicts: list[dict[str, Any]] = []
        merged_translations: dict[str, list[dict[str, Any]]] = {}

        src_tr = src_snap.get("translations") or {}
        tgt_tr = tgt_snap.get("translations") or {}
        langs = set(src_tr) | set(tgt_tr)

        for lang in langs:
            src_map = self._paras_by_id(src_tr.get(lang) or [])
            tgt_map = self._paras_by_id(tgt_tr.get(lang) or [])
            all_ids = set(src_map) | set(tgt_map)
            merged_list: list[dict[str, Any]] = []

            for pid in sorted(all_ids, key=lambda x: (len(x), x)):
                in_src = pid in src_map
                in_tgt = pid in tgt_map

                if in_src and not in_tgt:
                    merged_list.append(copy.deepcopy(src_map[pid]))
                elif in_tgt and not in_src:
                    merged_list.append(copy.deepcopy(tgt_map[pid]))
                else:
                    s_text = (src_map[pid].get("text") or "").strip()
                    t_text = (tgt_map[pid].get("text") or "").strip()
                    if s_text == t_text:
                        merged_list.append(copy.deepcopy(tgt_map[pid]))
                    else:
                        #наслоение: оба меняли один абзац по-разному
                        conflicts.append(
                            {
                                "paragraph_id": pid,
                                "lang": lang,
                                "reason": "both_modified",
                                "source_text": src_map[pid].get("text", ""),
                                "target_text": tgt_map[pid].get("text", ""),
                            }
                        )

            if merged_list:
                merged_translations[lang] = merged_list

        #source-абзацы: берём target как базу (типичный merge into target)
        merged_content: dict[str, Any] = {
            "source": copy.deepcopy(
                tgt_snap.get("source") or src_snap.get("source") or []
            ),
            "translations": merged_translations,
        }

        if conflicts:
            result = self._merge_result(
                ok=False,
                status="conflicts",
                message=f"Конфликтов: {len(conflicts)}",
                conflicts=conflicts,
                merged_content=None,
            )
            self.status_message.emit(
                f"Merge {source} → {target}: конфликты "
                + ", ".join(
                    f"{c['lang']}:{c['paragraph_id']}" for c in conflicts
                )
            )
            self._emit_merge(result, source, target)
            return result

        #успех: применяем к документу
        self._document["content"] = merged_content
        result = self._merge_result(
            ok=True,
            status="ok",
            message=f"Слияние {source} → {target} успешно",
            conflicts=[],
            merged_content=copy.deepcopy(merged_content),
        )
        self.status_message.emit(result["message"])
        self._emit_merge(result, source, target)
        return result

    def rollback_to_commit(self, commit_hash: str) -> None:
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
                "rollback content невозможен"
            )
            return

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

    #helpers

    def _find_commit(self, commit_hash: str) -> dict[str, Any] | None:
        if self._document is None:
            return None
        for c in self._document.get("version_history") or []:
            if str(c.get("commit_hash")) == commit_hash:
                return c
        return None

    @staticmethod
    def _paras_by_id(paragraphs: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
        return {str(p.get("paragraph_id")): p for p in paragraphs}

    @staticmethod
    def _merge_result(
        *,
        ok: bool,
        status: str,
        message: str,
        conflicts: list[dict[str, Any]] | None = None,
        merged_content: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return {
            "ok": ok,
            "status": status,
            "message": message,
            "conflicts": conflicts or [],
            "merged_content": merged_content,
        }

    def _emit_merge(
        self, result: dict[str, Any], source: str, target: str
    ) -> None:
        self.merge_finished.emit(result)
        self.merge_done.emit(source, target)
        if not result["ok"] and result["status"] == "error":
            self.error_occurred.emit(result["message"])
