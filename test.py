from llms.qwen import completion

with completion(
    model="qwen-max-latest",
    messages=[{"role": "user", "content": "Hello"}]
) as answer:
    print(answer['content'])
