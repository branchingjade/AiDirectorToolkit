// Token Monitor Plugin — correct pattern using bundled backend route
// Deployed at <repo>/plugins/token-monitor/dashboard/dist/index.js
// This is the VERSION THAT ACTUALLY WORKS.
//
// Key difference from the naive approach:
//   SDK.api.getSessions() does NOT return estimated_cost_usd / billing_provider / reasoning_tokens
//   (see SKILL.md Data section for the actual SessionInfo TypeScript interface).
//   Instead, use SDK.fetchJSON() to call a bundled plugin's backend route
//   that reads state.db directly.
//
// Prerequisites:
//   1. Plugin is in <repo-root>/plugins/token-monitor/dashboard/ (bundled)
//   2. manifest.json has "api": "plugin_api.py"
//   3. plugin_api.py exposes GET /stats endpoint (see references/bundled-plugin-pattern.md)
//   4. Dashboard restarted after placing files

(function() {
  "use strict";

  var SDK = window.__HERMES_PLUGIN_SDK__;
  if (!SDK) return;
  var React = SDK.React;
  var useState = SDK.hooks.useState;
  var useEffect = SDK.hooks.useEffect;
  var Card = SDK.components.Card;
  var CardHeader = SDK.components.CardHeader;
  var CardTitle = SDK.components.CardTitle;
  var CardContent = SDK.components.CardContent;
  var Badge = SDK.components.Badge;
  var Tabs = SDK.components.Tabs;
  var TabsList = SDK.components.TabsList;
  var TabsTrigger = SDK.components.TabsTrigger;

  function fmtNum(n) {
    if (n == null || n === 0) return "0";
    if (n >= 1e6) return (n / 1e6).toFixed(1) + "M";
    if (n >= 1e3) return (n / 1e3).toFixed(1) + "K";
    return n.toLocaleString();
  }
  function fmtCost(n) {
    if (n == null || n === 0) return "$0.00";
    return "$" + n.toFixed(4);
  }
  var COLORS = ["#3b82f6","#8b5cf6","#ec4899","#f59e0b","#10b981","#06b6d4","#ef4444","#6366f1"];

  // SVG bar chart — see SKILL.md for full implementation
  // ... (BarChart, HBarChart, StatCard components as before)

  function TokenMonitorPage() {
    var _s = useState(null), data = _s[0], setData = _s[1];
    var _l = useState(true), loading = _l[0], setLoading = _l[1];
    var _e = useState(null), error = _e[0], setError = _e[1];
    var _t = useState("daily"), tab = _t[0], setTab = _t[1];

    useEffect(function() {
      // Use fetchJSON to call the bundled plugin's backend route
      SDK.fetchJSON("/api/plugins/token-monitor/stats")
        .then(function(resp) { setData(resp); setLoading(false); })
        .catch(function(e) { setError(e.message); setLoading(false); });
    }, []);

    if (loading) return React.createElement("div", { className: "p-8" },
      React.createElement("p", { className: "text-muted-foreground animate-pulse" }, "Loading..."));
    if (error) return React.createElement("div", { className: "p-8" },
      React.createElement("p", { className: "text-destructive" }, error));
    if (!data || !data.total) return null;

    var t = data.total;
    var dailyBars = (data.daily||[]).map(function(d) {
      return { label: d.day, value: d.cost, valueLabel: fmtCost(d.cost) };
    });
    var modelBars = (data.by_model||[]).map(function(m, i) {
      return { label: (m.provider?m.provider+"/":"")+m.model, value: m.cost,
        valueLabel: fmtCost(m.cost)+" | "+fmtNum((m.input||0)+(m.output||0))+" tokens",
        color: COLORS[i%COLORS.length] };
    });

    // Render: stat cards + tabs + charts (see SKILL.md for full render)
    return React.createElement("div", null, "/* ... */");
  }

  window.__HERMES_PLUGINS__.register("token-monitor", TokenMonitorPage);
})();
