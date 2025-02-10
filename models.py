from dataclasses import dataclass

@dataclass
class VideoContent:
    title: str
    sections: list[dict]
    summary: str

@dataclass
class VideoProgress:
    current: int
    total: int
    status: str
