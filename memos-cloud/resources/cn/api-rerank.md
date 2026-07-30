# rerank API

对一组候选文档按与查询的相关性重新排序，常用于检索后处理。**它不是 searchMemory 的替代**：searchMemory 从用户记忆里召回，rerank 只对你已有的候选文本排序。

## 端点

```
POST https://memos.memtensor.cn/api/openmem/v1/rerank
```

## 必要参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `query` | string | 用于衡量相关性的查询 |
| `documents` | array | 候选文档文本列表 |

## 可选参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `model` | string | 重排模型，例如 `"memos-reranker-0.6b"` |
| `top_n` | int | 只返回相关性最高的前 N 条（对应 CLI `--top-n`） |

## 用法

### HTTP

```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://memos.memtensor.cn/api/openmem/v1"

data = {
    "model": "memos-reranker-0.6b",
    "query": "用户有什么兴趣爱好",
    "documents": [
        "用户喜欢打羽毛球",
        "用户在杭州做后端开发",
        "用户偏好简洁的回复风格",
        "用户比较喜欢酱香型白酒",
        "用户下周三要去北京出差"
    ]
}

res = requests.post(
    f"{BASE_URL}/rerank",
    headers={"Authorization": f"Token {API_KEY}", "Content-Type": "application/json"},
    json=data
)
print(res.json())
```

### cURL

```bash
curl "$MEMOS_BASE_URL/rerank" \
  -H "Authorization: Token $MEMOS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "memos-reranker-0.6b",
    "query": "用户有什么兴趣爱好",
    "documents": ["用户喜欢打羽毛球", "用户在杭州做后端开发"]
  }'
```

### CLI（验证用）

```bash
memos rerank "python 后端" "Flask guide" "React guide" --top-n 2 --format json
```

## 返回

返回按相关性排序的结果（每个文档对应一个相关性得分/索引）。具体字段以 API reference / OpenAPI 为准。

## 何时用、何时不用

| 场景 | 建议 |
|------|------|
| 已有一批候选片段（如外部 RAG 结果），想按相关性排序 | 用 rerank。 |
| 想从用户长期记忆里召回事实/偏好 | 用 `searchMemory`，不要用 rerank。 |
| 候选列表很短且顺序无所谓 | 不必引入 rerank。 |
