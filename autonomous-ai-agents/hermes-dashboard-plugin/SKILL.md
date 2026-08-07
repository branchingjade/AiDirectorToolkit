---
name: hermes-dashboard-plugin
description: Build UI plugins for the Hermes web dashboard — custom tabs, slots, and backend routes.
version: 1.0.0
tags: [hermes, dashboard, plugin, frontend, react]
related_skills: [hermes-monitoring]
---

# Hermes Dashboard Plugin Development

Build and deploy custom UI plugins for the Hermes web dashboard (`hermes dashboard`). Plugins add tabs, inject components into shell slots, replace built-in pages, and (when bundled) register FastAPI backend routes.

## When to Use

- User asks to add a custom tab/page to the Hermes dashboard
- User wants to monitor something in the dashboard (token usage, costs, custom metrics)
- User asks to extend or reskin the dashboard beyond themes

## Reference Files

- `references/token-monitor-plugin.js` — Working example using `fetchJSON` to call bundled backend route (correct pattern — NOT `getSessions()`)
- `references/bundled-plugin-pattern.md` — Complete backend+frontend pattern for bundled plugins with `plugin_api.py`
- `references/state-db-sessions-schema.md` — state.db sessions table schema (note: `estimated_cost_usd` etc. exist in DB but NOT in dashboard REST API)

## Quick Reference

### Directory Layout

```
~/.hermes/plugins/<name>/dashboard/
├── manifest.json        # required — tab config, icon, entry point
├── dist/
│   ├── index.js         # required — pre-built JS bundle (IIFE)
│   └── style.css        # optional — custom CSS
└── plugin_api.py        # ONLY for bundled plugins — backend FastAPI routes
```

### manifest.json

```json
{
  "name": "my-plugin",
  "label": "My Plugin",
  "icon": "Sparkles",
  "version": "1.0.0",
  "tab": {
    "path": "/my-plugin",
    "position": "after:sessions"
  },
  "entry": "dist/index.js",
  "css": "dist/style.css"
}
```

Available Lucide icons: Activity, BarChart3, Clock, Code, Database, Eye, FileText, Globe, Heart, KeyRound, MessageSquare, Package, Puzzle, Settings, Shield, Sparkles, Star, Terminal, Wrench, Zap.

### JS Bundle (IIFE pattern)

```js
(function() {
  "use strict";
  const SDK = window.__HERMES_PLUGIN_SDK__;
  const { React } = SDK;
  const { useState, useEffect } = SDK.hooks;
  const { Card, CardHeader, CardTitle, CardContent, Badge } = SDK.components;

  function MyPage() {
    return React.createElement(Card, null,
      React.createElement(CardHeader, null,
        React.createElement(CardTitle, null, "My Plugin")
      ),
      React.createElement(CardContent, null,
        React.createElement("p", null, "Hello")
      )
    );
  }

  window.__HERMES_PLUGINS__.register("my-plugin", MyPage);
})();
```

### SDK Surface

```
SDK.React                    // React instance (never import React directly)
SDK.hooks.useState           // Standard React hooks
SDK.hooks.useEffect
SDK.hooks.useMemo
SDK.components.Card          // shadcn/ui components
SDK.components.CardHeader
SDK.components.CardTitle
SDK.components.CardContent
SDK.components.Badge
SDK.components.Button
SDK.components.Tabs / TabsList / TabsTrigger
SDK.api.getSessions(limit)  // Fetch session data (includes token counts, costs)
SDK.api.getConfig()         // Fetch config
SDK.api.getStatus()         // Agent status
SDK.fetchJSON(url)          // Authed fetch for custom endpoints
SDK.utils.cn(...)           // Tailwind class merger
SDK.utils.timeAgo(ts)       // "5m ago" from unix timestamp
```

### Data from SDK.api.getSessions()

```typescript
// SessionInfo — the TypeScript interface at web/src/lib/api.ts:1633
{
  id, source, model, title,
  started_at, ended_at, last_active, is_active,
  message_count, tool_call_count,
  input_tokens, output_tokens,
  preview, parent_session_id
}
```

**IMPORTANT**: `SessionInfo` does NOT include `estimated_cost_usd`, `billing_provider`, `reasoning_tokens`, or `cost_status`. These columns exist in state.db's `sessions` table but the dashboard REST API filters them out. Using `SDK.api.getSessions()` for cost data will silently return `undefined` (costs show as `$0.00`).

### Getting cost data: bundled plugin + backend route

The only way to expose cost data to a dashboard plugin is a **bundled plugin** with `plugin_api.py` that reads state.db directly:

```
<repo-root>/plugins/<name>/dashboard/
├── manifest.json          # must include "api": "plugin_api.py"
├── dist/index.js          # calls SDK.fetchJSON("/api/plugins/<name>/stats")
└── plugin_api.py          # FastAPI router reading state.db via sqlite3
```

The JS bundle calls `SDK.fetchJSON("/api/plugins/<name>/stats")` which auto-injects the session auth token. The Python backend reads `estimated_cost_usd`, `billing_provider`, etc. from state.db and returns them as JSON.

See `references/bundled-plugin-pattern.md` for a complete backend route example.

## Critical Constraints

### Bundled vs User plugins

| Property | User (`~/.hermes/plugins/`) | Bundled (`<repo>/plugins/`) |
|----------|------|---------|
| UI (manifest + JS + CSS) | ✅ | ✅ |
| Backend routes (`plugin_api.py`) | ❌ ignored | ✅ auto-loaded |
| Deployment | Drop files, rescan | Restart dashboard after adding |

User-plugin `plugin_api.py` files are deliberately ignored (security: GHSA-5qr3-c538-wm9j). If your plugin needs backend data processing (cost aggregation, state.db queries), deploy it as a bundled plugin.

### Desktop App ≠ Web Dashboard

The Hermes Desktop app (`hermes desktop`) and the web dashboard (`hermes dashboard`) are **separate frontends** that both talk to the same backend:

- **Web Dashboard**: React SPA at `web/src/`, loads bundled+user dashboard plugins. Accessible at `http://127.0.0.1:<port>`.
- **Desktop App**: Electron app at `apps/desktop/src/`, has its own hardcoded sidebar navigation. Does NOT load web dashboard plugins. Its source changes need a full rebuild (`apps/desktop/release/win-unpacked/`).

Web dashboard plugins appear as tabs in the web dashboard's top navigation bar. They do NOT appear in the Desktop app's sidebar. To add a panel to the Desktop app, modify `apps/desktop/src/app/desktop-controller.tsx` (add route), `apps/desktop/src/app/routes.ts` (add route constant), `apps/desktop/src/app/chat/sidebar/index.tsx` (add SIDEBAR_NAV entry), `apps/desktop/src/app/types.ts` (add SidebarNavId), plus i18n and keybind entries — then rebuild the Desktop app.

### No React bundling

Plugins do NOT bundle React or UI components. Use `SDK.React` (React.createElement) and `SDK.components.*`. If using JSX, bundle with esbuild/Vite with React as external and IIFE output format.

### Chart rendering

The SDK does NOT include chart libraries. Use raw SVG in `React.createElement` calls — no external dependencies needed. See `references/token-monitor-plugin.js` for a complete example with BarChart and HBarChart SVG components.

## Testing

### Check if dashboard is running
```bash
curl -s http://127.0.0.1:9119/api/dashboard/plugins
```

### Start dashboard
```bash
hermes dashboard --no-open --port 9119
```

### Force plugin rescan (no restart needed after adding new files)
```bash
curl http://127.0.0.1:9119/api/dashboard/plugins/rescan
```

### Verify plugin assets are served
```bash
curl -s http://127.0.0.1:9119/dashboard-plugins/token-monitor/dist/index.js | head -3
```

### Open dashboard
http://127.0.0.1:9119 — the plugin tab appears in the top navigation bar.

## Critical Pitfalls

### ALWAYS clarify frontend BEFORE building
The user saying "加面板" or "加功能" is ambiguous. Ask: **"要加到 Hermes 桌面端侧边栏，还是 web dashboard 标签页？"** before writing any code. Desktop and web dashboard are completely separate frontends — guessing wrong wastes an entire session. See Desktop App ≠ Web Dashboard below.

### Bundled vs User plugins

- **Plugin not showing**: Check manifest.json is at `~/.hermes/plugins/<name>/dashboard/manifest.json` (note the `dashboard/` subdirectory). Call `/api/dashboard/plugins/rescan`.
- **JS bundle errors**: Open browser DevTools → Console. Common issues: `__HERMES_PLUGINS__ is undefined` (SDK didn't initialize, React render crash earlier), or the IIFE threw before calling `register()`.
- **Mismatched name**: `manifest.json:name` must match the first argument to `window.__HERMES_PLUGINS__.register(name, Component)`.
- **Browser redirects to Desktop app**: When using `hermes` browser tools, navigating to `127.0.0.1:9119` may route to the Hermes Desktop app instead of the web dashboard. The user should open the URL directly in their real browser. Verify with `curl` instead.
