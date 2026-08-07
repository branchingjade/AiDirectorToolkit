# robocopy on git-bash/MSYS

## Path conversion trap

MSYS auto-converts Unix-style paths and flags that look like paths.
`/MIR` → `C:/Program Files/Git/MIR` — breaks the command.

**Fix:**
```bash
export MSYS_NO_PATHCONV=1
robocopy "$(cygpath -w /c/Users/...)" "$(cygpath -w /c/Users/...)" /MIR ...
```

## Exit codes

robocopy uses bitmask exit codes:

| Code | Meaning |
|------|---------|
| 0 | No files copied |
| 1 | Files copied successfully |
| 2 | Extra files/dirs in destination (with /MIR: deleted) |
| 3 | 1+2 |
| 4 | Mismatched files |
| 8+ | Errors |

**Rule: `$? -le 7` = success.** Never `set -e` with robocopy.

## Key flags

| Flag | Purpose |
|------|---------|
| `/MIR` | Mirror source to destination |
| `/NP` | No progress (cleaner output) |
| `/NDL` | No directory list |
| `/NFL` | No file list |
| `/R:2 /W:3` | Retry 2 times, wait 3 seconds |
| `/XD dir1 dir2` | Exclude directories |
| `/XF "*.log"` | Exclude files by pattern |
