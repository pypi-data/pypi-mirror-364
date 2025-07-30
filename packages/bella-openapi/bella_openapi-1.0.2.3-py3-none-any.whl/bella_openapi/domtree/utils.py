import tiktoken

# 自研模型均用gpt-4计算（可能有误差，可忽略）
def count_tokens(text: str, model: str = "gpt-4") -> int:
    if not text:
        return 0
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)
    # 计算标记列表的长度，即标记的数量
    token_count = len(tokens)
    # 返回标记的数量
    return token_count