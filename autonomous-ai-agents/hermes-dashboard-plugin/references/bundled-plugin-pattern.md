# Bundled Dashboard Plugin — Backend Route Pattern

When a dashboard plugin needs data from state.db that isn't exposed by `SDK.api.getSessions()` (notably: `estimated_cost_usd`, `billing_provider`, `reasoning_tokens`), deploy as a **bundled plugin** with a `plugin_api.py` backend route.

## Directory structure

```
<repo-root>/plugins/<name>/dashboard/
├── manifest.json          # must include "api": "plugin_api.py"
├── dist/
│   ├── index.js           # IIFE, calls SDK.fetchJSON("/api/plugins/<name>/stats")
│   └── style.css
└── plugin_api.py          # FastAPI router, reads state.db via sqlite3
```

The repo root on a Hermes install is `~/.hermes/hermes-agent/` (Windows: `%LOCALAPPDATA%/hermes/hermes-agent/`).

## manifest.json (key additions)

```json
{
  "name": "token-monitor",
  "label": "Token 监看",
  "icon": "BarChart3",
  "tab": { "path": "/token-monitor", "position": "after:sessions" },
  "entry": "dist/index.js",
  "css": "dist/style.css",
  "api": "plugin_api.py"
}
```

The `"api"` field tells the dashboard server to import `plugin_api.py` and mount its router at `/api/plugins/<name>/`. Only bundled plugins (in `<repo>/plugins/`) get this treatment.

## plugin_api.py (backend)

```python
"""Backend routes at /api/plugins/<name>/"""
import os, sqlite3
from collections import defaultdict
from datetime import datetime
from fastapi import APIRouter

router = APIRouter()
HERMES_HOME = os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes"))

def _get_db():
    return sqlite3.connect(os.path.join(HERMES_HOME, "state.db"))

@router.get("/stats")
async def get_stats():
    db = _get_db()
    try:
        cur = db.cursor()
        cur.execute("""
            SELECT model, billing_provider, source, started_at,
                   input_tokens, output_tokens, reasoning_tokens,
                   estimated_cost_usd, cost_status, id, title, message_count
            FROM sessions ORDER BY started_at DESC
        """)
        cols = ["model","provider","source","started_at",
                "input_tokens","output_tokens","reasoning_tokens",
                "estimated_cost_usd","cost_status","id","title","message_count"]
        rows = cur.fetchall()

        total_cost = 0.0
        total_input = 0
        total_output = 0
        by_day = defaultdict(lambda: {"cost":0,"sessions":0})
        by_model = defaultdict(lambda: {"cost":0,"provider":""})
        recent = []

        for r in rows[:500]:
            d = dict(zip(cols, r))
            cost = d["estimated_cost_usd"] or 0
            inp = d["input_tokens"] or 0
            out = d["output_tokens"] or 0
            total_cost += cost
            total_input += inp
            total_output += out
            day = datetime.fromtimestamp(d["started_at"]).strftime("%m-%d")
            by_day[day]["cost"] += cost
            by_day[day]["sessions"] += 1
            model = d["model"] or "unknown"
            by_model[model]["cost"] += cost
            by_model[model]["provider"] = d["provider"] or ""
            if len(recent) < 20:
                recent.append({k: d[k] for k in ["id","title","model","source","started_at","input_tokens","output_tokens","estimated_cost_usd"]})

        return {
            "total": {"estimated_cost_usd": round(total_cost, 6), "input_tokens": total_input,
                       "output_tokens": total_output, "session_count": len(rows)},
            "daily": sorted([{"day":k,**v} for k,v in by_day.items()]),
            "by_model": sorted([{"model":k,**v} for k,v in by_model.items()], key=lambda x:-x["cost"]),
            "recent": recent
        }
    finally:
        db.close()
```

## JS bundle (frontend)

Replace `SDK.api.getSessions()` with `SDK.fetchJSON()`:

```js
useEffect(function() {
  SDK.fetchJSON("/api/plugins/token-monitor/stats")
    .then(function(resp) { setData(resp); setLoading(false); })
    .catch(function(e) { setError(e.message); setLoading(false); });
}, []);
```

`fetchJSON` auto-injects the dashboard session auth token. The response shape is defined by `plugin_api.py`, so you control exactly which fields are returned.

## Deploy & verify

1. Place files in `<repo>/plugins/<name>/dashboard/`
2. Kill and restart `hermes dashboard` (backend routes are mounted at startup, not on rescan)
3. Verify: `curl http://127.0.0.1:9119/api/dashboard/plugins` should show `"has_api": true, "source": "bundled"`
4. The plugin tab appears in the web dashboard's top nav

## Pitfall: user plugin with same name

If a user plugin (`~/.hermes/plugins/<name>/`) exists with the same name as the bundled plugin, the user version takes discovery priority (but `has_api` stays false). Delete the user version before deploying the bundled one.
