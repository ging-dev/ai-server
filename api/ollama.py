import json
from flask import Blueprint, request
from llms.qwen import completion

ollama_endpoint = Blueprint(name="ollama_api", import_name=__name__, url_prefix="/api")


@ollama_endpoint.post("/show")
def show():
    return {"template": "tools"}


@ollama_endpoint.post("/chat")
def chat():
    kwargs: dict = request.get_json(force=True)
    stream = bool(kwargs.pop("stream", not kwargs.get("tools")))
    if stream:

        def generate():
            with completion(**kwargs, stream=True) as stream_response:
                for chunk in stream_response:
                    yield json.dumps({"done": False, "message": chunk}) + "\n"
                yield json.dumps({"done": True, "done_reason": "stop"})

        return generate(), {"Content-Type": "application/x-ndjson"}

    with completion(**kwargs, stream=False) as message:
        return {"done": True, "done_reason": "stop", "message": message}
