# GitHub CLI on Windows

## Config location

On Windows, `gh` stores config at:
```
%APPDATA%\GitHub CLI\hosts.yml
```
NOT at `~/.config/gh/hosts.yml` (the Unix path).

MSYS path: `/c/Users/<user>/AppData/Roaming/GitHub CLI/hosts.yml`

## Token storage: keyring only

`gh` on Windows **always** stores the token in Windows Credential Manager (keyring).
The `hosts.yml` file only contains `user` and `git_protocol` — no token.

```
github.com:
    git_protocol: https
    user: branchingjade
```

`gh auth login --with-token` does NOT create a file-based token on Windows.
There is no flag to force file storage.

## Backing up GitHub token

Since the token is locked in keyring, the only way to back it up is to export it
as an environment variable and store it in a file that IS in scope.

### Method: export to `.env`

```bash
# User runs this in their own terminal (agent cannot read secrets due to redaction):
echo "GH_TOKEN=*** auth token)" >> ~/.hermes/.env
```

`gh` checks `GH_TOKEN` and `GITHUB_TOKEN` env vars before keyring, so this works
transparently. On restore, the env var takes priority.

## Secret redaction

Hermes redacts secrets (API keys, tokens) from ALL tool outputs — terminal,
read_file, and execute_code. Even base64-encoding does not bypass it.
The agent **cannot** programmatically extract a token from keyring or anywhere else.
All secret-transfer operations require the user to run the command directly.
