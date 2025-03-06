import json
import re
import httpx
import os
from contextlib import contextmanager
from typing import Iterator, Generator
from .typing import Message
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


@contextmanager
def completion(
    model: str, messages: list[Message], stream: bool = False, **kwargs
) -> Generator[Message | Iterator[Message], None, None]:
    for message in messages:
        if message["role"] == "tool":
            message["role"] = "user"
            message["content"] = f"<tool_response>{message['content']}</tool_response>"
    tools = kwargs.pop("tools", None)
    if tools and not stream:
        from jinja2 import Environment

        tools_template = Environment().from_string(TOOLS_PROMPT).render(tools=tools)
        first_message = messages[0]
        if first_message["role"] == "system":
            first_message["content"] += tools_template
        else:
            messages.insert(0, {"role": "system", "content": tools_template})

    try:
        client = httpx.Client(
            base_url="https://chat.qwen.ai/",
            headers={
                "Authorization": f"Bearer {os.environ['QWEN_TOKEN']}",
                "User-Agent": "GingTeam",
            },
        )
        completion_kwargs = {
            "method": "POST",
            "url": "/api/chat/completions",
            "json": {
                "model": model,
                "messages": messages,
                "stream": stream,
                "incremental_output": True,
            },
        }
        if stream:
            with connect_sse(client, **completion_kwargs) as response:
                yield (
                    chunk.json()["choices"][0]["delta"] for chunk in response.iter_sse()
                )
        else:
            response = client.request(**completion_kwargs)
            message: Message = response.json()["choices"][0]["message"]
            tool_calls = try_parse_tool_calls(message["content"])
            if tool_calls:
                message["content"] = ""
                message["tool_calls"] = tool_calls

            yield message

    finally:
        client.close()


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
