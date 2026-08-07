# Manual Skill Installation & GitHub Update

Covers workflows beyond `hermes skills install` — direct `.skill` file installation and GitHub-based updates for skills not in the hub.

## .skill File Format

A `.skill` file is a **ZIP archive** containing a skill directory with:
- `SKILL.md` (required) — frontmatter + body
- `EXAMPLES.md`, `REFERENCE.md` — optional support docs
- `references/`, `scripts/`, `versions/` — optional subdirectories

The ZIP may use backslash path separators (Windows convention).

## Manual Installation from .skill File

Target directory: `~/AppData/Local/hermes/skills/<skill-name>/` (Windows) or `~/.hermes/skills/<skill-name>/` (Linux/macOS).

### Pitfall: cp437 Filename Encoding

ZIP archives created on Windows often encode non-ASCII filenames (Chinese, Japanese, etc.) using **cp437** rather than UTF-8. The default Python `zipfile` and most CLI `unzip` tools will produce garbled filenames.

**Wrong approach** (garbles Chinese filenames):
```bash
unzip file.skill -d target/
```

**Correct approach** — use Python with explicit encoding:
```python
import zipfile, os, shutil

zip_path = "path/to/skill.skill"
target = os.path.expanduser("~/AppData/Local/hermes/skills/skill-name")

if os.path.exists(target):
    shutil.rmtree(target)
os.makedirs(target, exist_ok=True)

with zipfile.ZipFile(zip_path, 'r') as z:
    for info in z.infolist():
        # cp437 → UTF-8 for non-ASCII filenames
        try:
            fname = info.filename.encode('cp437').decode('utf-8')
        except:
            fname = info.filename

        # Strip top-level directory from ZIP
        parts = fname.split('/', 1)
        rel = parts[1] if len(parts) > 1 else None
        if not rel:
            continue

        out_path = os.path.join(target, rel)
        if info.is_dir():
            os.makedirs(out_path, exist_ok=True)
        else:
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            with z.open(info) as src, open(out_path, 'wb') as dst:
                dst.write(src.read())
```

Key steps:
1. `shutil.rmtree(target)` — clean install, avoids stale files
2. `encode('cp437').decode('utf-8')` — fix filename encoding
3. Strip top-level directory — ZIPs often wrap content in `skill-name/...`

### Verification

After install, verify with `skill_view(name)` or `hermes skills list`.

## GitHub-Based Skill Update

For skills maintained in a GitHub repo (not in the Hermes hub), use git to fetch the latest version.

### Workflow

```bash
# 1. Check available tags
git ls-remote https://github.com/OWNER/REPO | grep 'refs/tags/'

# 2. Shallow clone the latest tag
cd /tmp && rm -rf skill-repo
git clone --depth 1 --branch TAG_NAME https://github.com/OWNER/REPO

# 3. Copy skill directory to global skills
TARGET="$HOME/AppData/Local/hermes/skills/skill-name"  # or ~/.hermes/skills/
rm -rf "$TARGET" && mkdir -p "$TARGET"
cp -r /tmp/skill-repo/SKILL_DIR/* "$TARGET/"

# 4. Clean up
rm -rf /tmp/skill-repo
```

### Pitfalls

- **Private repos**: `git ls-remote` works without auth for public repos. For private repos, need `gh auth login` or SSH keys.
- **Tag naming**: Look for skill-specific tags (e.g. `ai-director-assistant-v11.0.0`) rather than generic version tags.
- **Directory structure mismatch**: The skill files may be in a subdirectory of the repo, not at root. Check with `find . -name SKILL.md`.

## Alternative: hermes skills tap

For recurring updates from a GitHub repo, register it as a skill source:

```bash
hermes skills tap add OWNER/REPO
hermes skills install SKILL_NAME
hermes skills check  # check for updates
hermes skills update # apply updates
```

This is the preferred approach for skills you'll update regularly. Manual installation is for one-off installs or when `tap` isn't available.
