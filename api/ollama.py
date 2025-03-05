import json
from flask import Blueprint, request
from llms.qwen import completion, try_parse_tool_calls
from llms.typing import ChatRequest

ollama_endpoint = Blueprint(name="api", import_name=__name__, url_prefix="/api")


@ollama_endpoint.post("/show")
def show():
    return {"template": "tools"}


@ollama_endpoint.post("/chat")
def chat():
    kwargs: ChatRequest = request.get_json(force=True)
    stream = kwargs.get("stream", False if kwargs.get("tools") else True)

    def generate():
        content = ""
        for chunk in completion(**kwargs):
            content += chunk["content"]
            if kwargs.get("stream", True):
                yield json.dumps({"done": False, "message": chunk}) + "\n"
        final = {"done": True, "done_reason": "stop"}
        if not stream:
            message = {
                "role": chunk["role"],
                "content": content,
            }
            tool_calls = try_parse_tool_calls(content)
            if tool_calls:
                message["content"] = ""
                message["tool_calls"] = tool_calls
            final["message"] = message
        yield json.dumps(final)

    return generate(), {
        "Content-Type": "application/" + ("x-ndjson" if stream else "json")
    }
