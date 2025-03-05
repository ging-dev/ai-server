import json
import re
import httpx
import os
from typing import Unpack, Iterator
from .typing import ChatRequest, Message
from httpx_sse import connect_sse

TOOLS_PROMPT = """
# Tools

You may call one or more functions to assist with the user query.

You are provided with function signatures within <tools></tools> XML tags:
<tools>
{% for tool in tools %}
    {{ tool|tojson }}
{% endfor %}
</tools>

For each function call, return a json object with function name and arguments within <tool_call></tool_call> XML tags:
<tool_call>
{"name": <function-name>, "arguments": <args-json-object>}
</tool_call>
"""


def completion(**completion_kwargs: Unpack[ChatRequest]) -> Iterator[Message]:
    completion_kwargs["stream"] = True
    completion_kwargs["incremental_output"] = True
    for msg in completion_kwargs["messages"]:
        if msg["role"] == "tool":
            msg["role"] = "user"
            msg["content"] = f"<tool_response>{msg["content"]}</tool_response>"
    tools = completion_kwargs.pop("tools", None)
    if tools:
        from jinja2 import Environment

        template = Environment().from_string(TOOLS_PROMPT)
        first_msg = completion_kwargs["messages"][0]
        if first_msg["role"] == "system":
            first_msg["content"] += template.render(tools=tools)
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


def try_parse_tool_calls(content: str):
    tool_calls = []
    for m in re.finditer(r"<tool_call>\n(.+)?\n</tool_call>", content):
        try:
            func = json.loads(m.group(1))
            tool_calls.append({"function": func})
        except json.JSONDecodeError as e:
            print(f"Failed to parse tool calls: the content is {m.group(1)} and {e}")

    return tool_calls


__all__ = ["completion", "try_parse_tool_calls"]
