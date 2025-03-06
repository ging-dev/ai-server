from typing import ContextManager, Iterator, Literal, overload
from .typing import Message

@overload
def completion(
    model: str, messages: list[Message], stream: Literal[False] = False, **kwargs
) -> ContextManager[Message]: ...
@overload
def completion(
    model: str, messages: list[Message], stream: Literal[True], **kwargs
) -> ContextManager[Iterator[Message]]: ...
