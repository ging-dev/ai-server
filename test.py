from llms.qwen import completion

for chunk in completion(
    model="qwen-max-latest",
    stream=True,
    incremental_output=True,
    messages=[{"role": "user", "content": "What's the weather like in Boston today?"}],
):
    print(chunk["content"], end="")
