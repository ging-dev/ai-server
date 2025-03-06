from llms.qwen import completion

with completion(
    model="qwen-max-latest",
    stream=False,
    messages=[{"role": "user", "content": "Hello"}],
) as answer:
    print(answer['content'])
