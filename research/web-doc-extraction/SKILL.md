---
name: web-doc-extraction
description: >
  Batch extraction of structured technical documentation (API parameters, endpoints, 
  response formats, config references) from online documentation pages using the 
  browser toolset. Covers rapid multi-page crawling with browser_navigate → 
  browser_snapshot(full=true) → read_file, sub-page drill-down on index/overview 
  pages, and structured output to a local file. NOT for general web scraping — 
  reserved for documentation-centric extraction tasks where the user names specific 
  URLs.
trigger: |
  - User provides N URL(s) and asks to "extract key API parameters/endpoints/response format"
  - "go grab these docs URLs", "capture these pages", "extract API reference from these pages"
  - Batch crawling documentation sites for structured technical reference data
category: research
version: 1.0.0
---

# Web Documentation Extraction

Extract structured technical documentation (API params, endpoints, response schemas) from web documentation pages via the browser toolset.

## Workflow

Choose the extraction method based on what you need:

### Method A: Snapshot-based (DOM structure preserved)
Use when you need table structures, headings hierarchy, or element relationships.

### Method B: Console-based (full raw text)
Use when you need the complete page text without truncation, or the snapshot is too large to manage.

### 1. Prepare output file
Create the destination file first so you can append incrementally:

```python
# Create with header
write_file(path="hermes-output/batch_d.txt", content="# Documentation Extraction\n")
```

### 2A. Navigate → Snapshot → Read loop (Method A)

For each URL, execute in rapid succession (≤3 second pauses):

```
browser_navigate(url)          # Gets compact snapshot
browser_snapshot(full=true)    # Full snapshot saved to cache file
read_file(snapshot_path)       # Read the full snapshot from cache, with offset+limit for large files
```

**Key details:**
- `browser_navigate` returns a compact snapshot in the response body — use this for initial assessment
- `browser_snapshot(full=true)` saves the COMPLETE page content to a temp file under `AppData\Local\hermes\cache\web\`
- The snapshot path is in `browser_navigate` output when content is truncated: `read_file path="..." offset=N`
- For large snapshots, read in chunks using `offset` + `limit` (default 500 lines)
- After reading, immediately write extracted data and navigate to next page (parallelize write + navigate when possible)

### 2B. Navigate → Wait → Console extract loop (Method B)

For each URL, execute with a rendering pause:

```
browser_navigate(url)
terminal(sleep 3)              # Wait for SPA/js rendering (3s is usually sufficient)
browser_console(clear=true, expression="document.body.innerText")
```

**Key details:**
- `browser_console` with `document.body.innerText` returns the COMPLETE rendered text — no truncation, no file to read
- **No `browser_snapshot` needed** — the console approach is faster and handles very long pages (tested up to 70K+ bytes)
- The 3-second wait after navigate is critical for SPA docs sites (like Volcengine) — the page needs time to render
- After extracting, write the result and immediately navigate to next page
- Use `clear=true` to keep each page's console fresh

### 3. Extract structured data from the accessibility tree

The snapshot output is an indented accessibility tree. Key patterns to grep for:

| Pattern | What to extract |
|---------|----------------|
| `heading` | Section titles (endpoint names) |
| `columnheader` / `cell` | Table structures — parameter tables |
| `code` blocks | Request/response JSON examples |
| `strong` | HTTP methods (GET/POST) |
| `link` + `menuitem` | Sub-page navigation on index pages |

**Table reconstruction:** Tables appear as `rowgroup > row > cell` sequences. Walk adjacent rows to rebuild the parameter table. Each `cell` has a `StaticText` child with the value.

**Code blocks:** Have `StaticText` children with the full code/schema content. Join adjacent lines.

### 4. Sub-page drill-down (common on doc index pages)

When an overview/index page lists links to sub-pages (e.g., "API Key使用" → links to "ListAPIKeys - 拉取APIKey列表", "CreateAPIKey - 创建APIKey"):

1. Capture the index page's menu structure (shows which sub-APIs exist)
2. Click through to EACH sub-page with `browser_click(ref=...)` 
3. Apply the same snapshot → read → extract loop per sub-page
4. Navigate back or use the menu to reach the next sub-page

The left-nav menu stays open across clicks — use the menu's `link`/`menuitem` refs to navigate between sub-pages.

### 5. Output formatting conventions

Two formats are available:

**Format A — Full detail (for API docs):**
- Per-page section: `## [N] Page Title` then `### URL: <url>` then `### 基本信息` then structured tables
- Use Markdown tables for parameter/schema documentation:
  ```
  | Parameter | Type | Required | Location | Description |
  ```
- Use `code` blocks for request/response JSON examples
- Separate pages with `---` dividers
- Include error codes and examples where available

**Format B — Compact page separator (for raw-text batch extraction):**
- When the user names a target file or you're extracting many pages of raw text
- Use `===PAGE(N): <URL>===` as a clear page separator
- Follow each separator with the full extracted innerText of that page
- This format works best with Method B (console extraction) since the content is already plain text

### 6. User-specified filename output format

When the user names a target file (e.g. `verify_c.txt`, `extract_d.txt`), use this format:

- **Module separator:** `=== Module Name ===`
- **Source page identifier:** `【源StaticText】<page heading from snapshot>`
- **Protocol/endpoint:** `【端点】<url>` with HTTP method prefix  
- **Tables by category:**
  - `【请求头参数表】` — Header parameters
  - `【请求体参数表】` — Body/payload parameters (with nesting via dot-notation: `Params.xxx.yyy`)
  - `【响应体/响应结构】` — Response fields
  - `【事件定义】` — WebSocket event codes (protocol-specific)
  - `【错误码】` — Error code table
- **WebSocket-specific:** Always include event definition tables + binary frame structure notes
- **Multi-endpoint APIs:** Separate submit and query endpoints with distinguishing sub-headers
- **Column order for parameter tables:** consistently: 字段/参数名 | 说明 | 是否必须 | 类型 | 默认值/备注

## Pitfalls

- **Truncated snapshots:** `browser_navigate` truncates at ~15K chars. Always call `browser_snapshot(full=true)` immediately after navigate to get the complete file saved to cache.
- **Wrote wrong file / stale snapshot:** After navigating to a NEW page, the previous snapshot file remains on disk. Always read the snapshot path returned in *this* navigate's output, not a path from a prior turn.
- **Overlap in research-skills:** This skill overlaps with `analysis-report` (report writing from gathered data) and `computer-use` (general desktop browser driving). Use this skill specifically for **batch extraction of structured technical reference data from named URLs** — not for writing analysis reports from the extracted data (that's `analysis-report`) or for general web browsing.
- **SPA rendering timing (console method):** When using Method B (console-based), the page's JavaScript needs time to render content. Use `terminal(sleep 3)` between `browser_navigate` and `browser_console` extraction. For very heavy SPA pages, increase to 5s. Without the wait, `document.body.innerText` may return empty or partial content.
- **console method vs snapshot method:** `browser_console` innerText returns the exact rendered text your browser sees, but loses all DOM structure (you can't distinguish headings from body text, table cells from labels). Choose Method A when you need structure, Method B when you need complete raw text quickly.
- **Sub-page navigation timing:** Allow ~1-2 seconds between `browser_click` and `browser_snapshot` for the page's JS to render the new content.
- **Parallelism:** You can batch `write_file` (append new section) + `browser_navigate` (next page) in the same response turn to stay under the 3-second page gap requirement.
- **Large responses:** When response has `quota_monitoring` or `usage_monitoring` arrays with many entries, summarize the structure and note the array length rather than dumping every row.

## References

- `references/batch-d-output-sample.md` — example output format from a 5-page Volcano Engine API doc extraction
- `references/volcengine-4page-params-extraction.md` — 4-page speech API extraction with both HTTP and WebSocket endpoints (user-specified filename format)
- `references/volcengine-asr-5page-endpoints.md` — 5-page ASR/端到端 API reference: verified URLs, resource IDs, protocol details, auth headers, parameter table patterns, client/server event lists for all Volcengine Doubao speech recognition and real-time dialogue APIs

## Related Skills

- `analysis-report` — writing structured analysis/report documents from gathered data (use AFTER extraction)
- `computer-use` — general desktop browser automation (broader use, less structured)
