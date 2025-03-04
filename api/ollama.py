import json
from flask import Blueprint, request
from llms.qwen import completion
from llms.typing import ChatRequest

ollama_endpoint = Blueprint(name="api", import_name=__name__, url_prefix="/api")


@ollama_endpoint.get("/show")
def show():
    return {"template": "tools"}


@ollama_endpoint.post("/chat")
def chat():
    kwargs: ChatRequest = request.get_json(force=True)
    stream = kwargs.get("stream", True)

    def generate():
        content = ""
        for chunk in completion(**kwargs):
            content += chunk["content"]
            if kwargs.get("stream", True):
                yield json.dumps({"done": False, "message": chunk}) + "\n"
        yield json.dumps(
            {
                "done": True,
                "message": {
                    "role": chunk["role"],
                    "content": content,
                },
            }
        )

    return generate(), {
        "Content-Type": "application/" + ("x-ndjson" if stream else "json")
    }
