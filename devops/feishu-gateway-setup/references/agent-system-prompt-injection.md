# agent.system_prompt Injection Trace

Verified 2026-07-02 on hermes-agent source.

## Injection Flow

```
config.yaml: agent.system_prompt
  ↓
gateway/run.py:2581  self._ephemeral_system_prompt = self._load_ephemeral_system_prompt()
  ↓
gateway/run.py:4303  _load_ephemeral_system_prompt()
                       reads from HERMES_EPHEMERAL_SYSTEM_PROMPT env var (priority)
                       OR agent.system_prompt in config.yaml (fallback)
  ↓
gateway/run.py:16149  combined_ephemeral = context_prompt or ""
                       context_prompt from build_session_context_prompt()
                       (contains **User:** / **Session type:**)
  ↓
gateway/run.py:16153  if self._ephemeral_system_prompt:
                         combined_ephemeral += "\n\n" + self._ephemeral_system_prompt
  ↓
gateway/run.py:16413  AIAgent(ephemeral_system_prompt=combined_ephemeral, ...)
```

## Session Context (injected alongside)

Built by `build_session_context_prompt()` in `gateway/session.py:275`:

- DM: `**User:** <display_name>` (line 370)
- Group: `**Session type:** Multi-user session — messages are prefixed with [sender name]` (line 365-367)

The agent sees BOTH the memory rules AND the user/session type in the same ephemeral system prompt, enabling personality-level gating.

## Key Source Files

| File | Lines | What |
|------|-------|------|
| `gateway/run.py` | 2581, 4303-4313 | Loads `agent.system_prompt` |
| `gateway/run.py` | 16147-16154 | Combines context + ephemeral |
| `gateway/run.py` | 16405-16413 | Passes to AIAgent |
| `gateway/session.py` | 275-375 | Builds session context with User/Session type |

## Verification

To confirm `agent.system_prompt` is loaded, check after gateway start:

```bash
grep "agent.system_prompt" ~/AppData/Local/hermes/config.yaml
```

Restart required: `hermes gateway stop && hermes gateway start`

## What does NOT work

- **`~/.hermes/SOUL.md`**: Zero references in hermes-agent source. Dead file.
- **`display.platforms.feishu.system_prompt`**: Different injection path, feishu-only. Use `agent.system_prompt` for universal coverage.
