import enum
from typing import Any


class MessageStatus(enum.Enum):
    pending = 'В очереди на отправку'
    sent = 'Отправлено'
    failed = 'Ошибка отправки'
    timed_out = 'Не успели отправить'

    @classmethod
    def as_model_choices(cls) -> list[tuple[str, Any]]:
        return [(item.name, item.value) for item in cls]

    @classmethod
    def as_names_list(cls) -> list[str]:
        return [item.name for item in cls]
