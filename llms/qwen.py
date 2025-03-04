import json
import httpx
import os
from typing import Unpack, Iterator
from .typing import ChatRequest, Message
from httpx_sse import connect_sse


def completion(**completion_kwargs: Unpack[ChatRequest]) -> Iterator[Message]:
    completion_kwargs["stream"] = True
    completion_kwargs["incremental_output"] = True

    with httpx.Client(
        base_url="https://chat.qwen.ai/",
        headers={
            "Authorization": f"Bearer {os.environ['QWEN_TOKEN']}",
            "User-Agent": "GingTeam",
        },
    ) as client:
        with connect_sse(
            client, "POST", "/api/chat/completions", json=completion_kwargs
        ) as response:
            for chunk in response.iter_sse():
                yield json.loads(chunk.data)["choices"][0]["delta"]


__all__ = ["completion"]
