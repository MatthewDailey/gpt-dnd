# first line: 14
@memory.cache
def openai_request(messages, model, temperature, cache_buster=None):
    start = time.time()
    result = openai.ChatCompletion.create(
        model=model,
        temperature=temperature,
        messages=messages,
        # max_tokens=4096,
    )
    print(f"Total time: {time.time() - start}")
    return result
