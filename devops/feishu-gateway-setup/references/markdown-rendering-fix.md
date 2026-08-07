# Feishu Markdown Rendering

## Actual code behavior (verified 2026-07-10)

`_build_outbound_payload` in `adapter.py` (code lives under `plugins/platforms/feishu/adapter.py`):

```python
def _build_outbound_payload(self, content: str) -> tuple[str, str]:
    if _MARKDOWN_HINT_RE.search(content):
        return "post", _build_markdown_post_payload(content)
    return "text", json.dumps({"text": content}, ...)
```

**Logic**: post format (markdown rendered) fires when `_MARKDOWN_HINT_RE` matches. Plain text without any markdown syntax → `text` format → no rendering.

⚠️ **Documentation is NOT authoritative — always verify source code.** The `_MARKDOWN_TABLE_RE` force-text block and the `_make_rows()` fix were documented as applied on 2026-07-01 but were NOT present in the actual adapter.py until 2026-07-10. When debugging rendering issues, read `_build_outbound_payload` and `_build_markdown_post_rows` directly rather than trusting this document's status claims.

### Quick verification script

Run in the hermes-agent tree:

```python
import sys; sys.path.insert(0, ".")
from plugins.platforms.feishu.adapter import _build_markdown_post_rows, _make_rows

content = "## 标题\n\n| A | B |\n|---|---|\n| 1 | 2 |\n\n- 列表项"
rows = _build_markdown_post_rows(content)
for i, row in enumerate(rows):
    assert "\n\n" not in row[0]["text"], f"Row {i} has blank line inside!"
print(f"OK: {len(rows)} rows, all single-paragraph")
```

`_MARKDOWN_HINT_RE` matches:
- `#` headings, `-`/`*` lists, `1.` ordered lists
- `---` horizontal rules, ``` code fences, `` ` `` inline code
- `**bold**`, `~~strikethrough~~`, `<u>underline</u>`, `*italic*`
- `[links](url)`, `>` blockquotes
- `|` pipe tables (table separator line triggers markdown hint match)

## `_build_markdown_post_rows` — md element single-paragraph constraint (CRITICAL)

Feishu's post message format: **each `md` tag supports only ONE paragraph.** Multi-paragraph content (containing blank lines / `\n\n`) inside a single `md` element causes the ENTIRE element to fail parsing and render as plain text.

The fix (applied 2026-07-10 in `adapter.py`):

- New helper `_make_rows(text)` splits content on `\n{2,}` (blank lines) and wraps each non-empty paragraph in its own `[{"tag": "md", "text": "..."}]` row
- Content without code fences: passed through `_make_rows()` directly
- Content with code fences: each flushed segment goes through `_make_rows()` via `rows.extend(_make_rows(segment))`

**Before fix**: `**bold**\n\n*italic*` → one `md` element → plain text garbage
**After fix**: `**bold**\n\n*italic*` → two separate `md` elements → both render correctly

Code change at `adapter.py` `_build_markdown_post_rows`. Requires `hermes gateway restart` after applying.

## Pitfalls

- **Entire message in code block**: If agent wraps the whole response in ```triple backticks```, Feishu renders EVERYTHING in monospace. Use `##` headings and `-` bullets for structure, only use ``` for actual code snippets.
- **Tables (FIXED 2026-07-10)**: The `_MARKDOWN_TABLE_RE` force-text block at `adapter.py:_build_outbound_payload` was removed on 2026-07-10 (previously documented as fixed on 07-01 but the code change was never applied):
  ```python
  # REMOVED (was in _build_outbound_payload):
  # if _MARKDOWN_TABLE_RE.search(content):
  #     text_payload = {"text": content}
  #     return "text", json.dumps(text_payload, ensure_ascii=False)
  ```
  Tables now fall through to `_MARKDOWN_HINT_RE` (pipe `|` triggers the markdown hint), get `msg_type=post`, and render correctly. Also updated the stale comment on line 159 of adapter.py.
- **Multi-paragraph in one `md` element**: ⚠️ This was the root cause of multi-paragraph messages rendering as plain text before the `_make_rows()` fix (see above). The fix is in code — the agent does NOT need to manually split paragraphs; `_build_markdown_post_rows` handles it automatically.
- **Gateway restart required**: After editing adapter.py, `hermes gateway restart` to take effect.
