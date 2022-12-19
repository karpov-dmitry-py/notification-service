from dataclasses import dataclass, asdict


@dataclass
class NotificationMessage:
    """
    Fbrq client notification message
    """
    id: int
    phone: str
    text: str

    def as_dict(self):
        return asdict(self)
