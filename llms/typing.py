from typing import TypedDict, List


class Message(TypedDict):
    role: str
    content: str


class ChatRequest(TypedDict):
    stream: bool
    incremental_output: bool
    model: str
    messages: List[Message]
