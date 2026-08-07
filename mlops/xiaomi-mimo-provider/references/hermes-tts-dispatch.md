# Hermes TTS Dispatch Architecture (discovered 2026-06-26)

## Provider Resolution Chain

When `tts.provider` is set in `~/.hermes/config.yaml`, `tools/tts_tool.py` resolves
the active provider through this chain:

```
1. COMMAND PROVIDER     → tts.providers.<name>: type: command in config.yaml
                          If found, runs shell command template.
2. PLUGIN REGISTRY      → agent.tts_registry.get_provider(name)
                          Plugin-registered TTSProvider instances.
3. BUILT-IN PROVIDERS   → elif chain: elevenlabs / openai / minimax / xai /
                          mistral / gemini / neutts / piper / kittentts
4. FALLBACK (default)   → Edge TTS (free, no API key)
```

## Where xiaomi/mimo fits

`xiaomi` is NOT in `BUILTIN_TTS_PROVIDERS` (frozenset: edge, openai, elevenlabs,
minimax, xai, mistral, gemini, neutts, kittentts, piper).

It reaches the dispatch at step 2 (plugin registry). A bundled plugin under
`hermes-agent/plugins/` calls `ctx.register_tts_provider()` at discovery time
with a `TTSProvider` whose `.name == "xiaomi"`.

## Plugin Discovery

`hermes_cli/plugins.py::_discover_and_load_inner()` scans:

1. Bundled: `<hermes-agent>/plugins/` (skips `model-providers/`, `memory/`,
   `context_engine/`, `platforms/` at top level)
2. User: `~/.hermes/plugins/`
3. Project: `./.hermes/plugins/` (if `HERMES_ENABLE_PROJECT_PLUGINS=1`)
4. Entry points: pip-installed packages

## TTS Error Format

```python
# tools/tts_tool.py line 2438
error_msg = f"TTS generation failed ({provider}): {e}"
```

The `{provider}` in the error message is the CONFIGURED provider name, not
necessarily the one that actually handled the request.

## Xiaomi TTS Specifics

- MiMo `/v1/audio/speech` returns 404 — MiMo does NOT use OpenAI TTS format
- The plugin talks to MiMo's proprietary TTS endpoint (not documented publicly)
- Key validity can be tested via `/v1/chat/completions` independently of TTS
- Log: `C:\Users\HMSJ\AppData\Local\hermes\logs\agent.log` shows TTS results

## Debugging Recipe

```bash
# 1. Test key
curl -s "$XIAOMI_BASE_URL/chat/completions" \
  -H "api-key: $XIAOMI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"mimo-v2.5","messages":[{"role":"user","content":"hi"}],"max_tokens":10}'

# 2. List TTS models (should include mimo-v2.5-tts)
curl -s "$XIAOMI_BASE_URL/models" -H "api-key: *** 
# 3. If key is valid but TTS fails, the plugin path is broken
#    → fallback: hermes config set tts.provider edge
```
