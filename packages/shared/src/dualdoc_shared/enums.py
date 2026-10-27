"""Общие перечисления."""
from enum import Enum


class ParagraphStatus(str, Enum):
    NOT_TRANSLATED = "not_translated"
    IN_PROGRESS = "in_progress"
    TRANSLATED = "translated"
    CHANGED = "changed"
    APPROVED = "approved"

class Role(str, Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    TRANSLATOR = "translator"
    OBSERVER = "observer"
