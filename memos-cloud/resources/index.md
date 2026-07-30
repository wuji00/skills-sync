# MemOS Cloud Resource Router

Choose one locale-specific docs index before reading task resources.

| User or deliverable language | Read |
| --- | --- |
| Chinese / 中文 | [cn/index.md](cn/index.md) |
| English | [en/index.md](en/index.md) |

Rules:

- Use the user's requested output language when it is explicit.
- If the user writes in Chinese, use `cn/` resources.
- If the user writes in English, use `en/` resources.
- If the request mixes languages, use the language of the artifact being produced.
- Keep API names, endpoint paths, SDK method names, field names, and file names unchanged across locales.
- Root-level `resources/*.md` should only contain this router. Task resources live under `resources/cn/` and `resources/en/`.
