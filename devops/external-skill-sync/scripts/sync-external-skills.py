#!/usr/bin/env python3
"""Sync external skills from tapped GitHub repos into Hermes skills directory.

Auto-discovers sources from hermes_skill_sources.yaml + hermes skills tap list.
Detects repo format (nested / flat / single) and syncs accordingly.
Outputs JSON to stdout for LLM parsing; human-readable summary to stderr.

Cron-friendly: script=scripts/sync-external-skills.py, no_agent=true
"""
import json
import os
import stat
import sys
import shutil
import subprocess
from pathlib import Path

SKILLS_DST = Path.home() / "AppData" / "Local" / "hermes" / "skills"
TMP_BASE = Path("/tmp")

# Repo config — populated by load_sources(), not hardcoded
REPOS = {}


def load_sources():
    """Load sources from hermes_skill_sources.yaml + hermes skills tap list."""
    sources_yaml = Path.home() / "AppData" / "Local" / "hermes" / "hermes_skill_sources.yaml"
    if sources_yaml.exists():
        try:
            import yaml
            with open(sources_yaml) as f:
                data = yaml.safe_load(f)
            for src in data.get("sources", []):
                repo_url = src["repo_url"]
                REPOS[repo_url] = {
                    "categories": src.get("categories", []),
                    "dst_prefix": src.get("prefix", repo_url.rstrip("/").split("/")[-1].replace(".git", "")),
                    "skills_subpath": src.get("skills_subpath", "skills"),
                }
        except Exception as e:
            print(f"\u26a0\ufe0f 无法读取 hermes_skill_sources.yaml: {e}", file=sys.stderr)

    # Also parse hermes skills tap list
    try:
        result = subprocess.run(
            ["hermes", "skills", "tap", "list"],
            capture_output=True, text=True, timeout=15
        )
        for line in result.stdout.strip().split("\n"):
            line = line.strip()
            if line and not line.startswith("No taps"):
                parts = line.split()
                # Table format has box-drawing chars — find the http(s) token
                url = None
                for part in parts:
                    if part.startswith("http://") or part.startswith("https://"):
                        url = part
                        break
                if url and url not in REPOS:
                    REPOS[url] = {
                        "categories": [],
                        "dst_prefix": url.rstrip("/").split("/")[-1].replace(".git", ""),
                        "skills_subpath": "skills",
                    }
    except Exception:
        pass

    # Default: always include mattpocock/skills if nothing else found
    if not REPOS:
        REPOS["https://github.com/mattpocock/skills.git"] = {
            "categories": ["engineering", "productivity", "misc", "in-progress", "personal"],
            "dst_prefix": "mattpocock",
            "skills_subpath": "skills",
        }


def rmtree_force(path):
    """Remove a directory tree, handling Windows permission issues.

    On Windows, .git/objects/pack/*.idx files are read-only and shutil.rmtree
    fails with PermissionError. This onerror handler chmods +w and retries.
    """
    def on_error(func, p, exc_info):
        os.chmod(p, stat.S_IWRITE)
        func(p)
    shutil.rmtree(str(path), onerror=on_error)


def clone(repo_url, clone_dir):
    clone_dir = Path(clone_dir)
    if clone_dir.exists():
        rmtree_force(clone_dir)
    subprocess.run(
        ["git", "clone", "--depth", "1", repo_url, str(clone_dir)],
        check=True, capture_output=True, text=True,
    )
    return clone_dir


def detect_format(clone_dir, cfg):
    """Detect repo format and return (format, categories, src_base).

    Formats:
      - nested:  skills/<category>/<skill>/SKILL.md  (mattpocock style)
      - flat:    <root>/*/SKILL.md                    (loose skill dirs)
      - single:  <root>/*.md                          (bare .md files)
      - unknown: nothing recognizable found
    """
    skills_subpath = cfg.get("skills_subpath", "skills")
    src_base = clone_dir / skills_subpath

    # Format: nested (skills/engineering/foo/SKILL.md)
    if src_base.is_dir() and any(
        d.is_dir() and any(d.rglob("SKILL.md"))
        for d in src_base.iterdir()
    ):
        categories = cfg.get("categories") or [
            d.name for d in src_base.iterdir() if d.is_dir()
        ]
        return "nested", categories, src_base

    # Format: flat (skill dirs with SKILL.md under skills_subpath)
    if src_base.is_dir() and any(
        item.is_dir() and (item / "SKILL.md").exists()
        for item in src_base.iterdir()
    ):
        categories = cfg.get("categories") or []
        return "flat", categories, src_base

    # Format: single .md files at root (e.g. AI-Skills)
    root_md = list(clone_dir.glob("*.md"))
    if root_md:
        return "single", [clone_dir.name], clone_dir

    return "unknown", [], None


def sync_nested(categories, src_base, dst_prefix):
    """Sync nested format: copy category dirs (e.g. mattpocock)."""
    results = []
    for cat in categories:
        src = src_base / cat
        dst = SKILLS_DST / f"{dst_prefix}-{cat}"
        if src.is_dir():
            if dst.exists():
                rmtree_force(dst)
            shutil.copytree(src, dst)
            count = len(list(dst.rglob("SKILL.md")))
            results.append({"category": cat, "skills": count, "status": "ok"})
    return results


def sync_flat(categories, src_base, dst_prefix):
    """Sync flat format: copy individual skill dirs to a common parent."""
    results = []
    dst_parent = SKILLS_DST / dst_prefix
    dst_parent.mkdir(parents=True, exist_ok=True)

    items_to_sync = []
    if categories:
        for cat in categories:
            item = src_base / cat
            if item.is_dir():
                items_to_sync.append(item)
    else:
        items_to_sync = sorted(
            item for item in src_base.iterdir()
            if item.is_dir() and (item / "SKILL.md").exists()
        )

    for item in items_to_sync:
        dst = dst_parent / item.name
        if dst.exists():
            rmtree_force(dst)
        shutil.copytree(item, dst)
        results.append({"category": item.name, "skills": 1, "status": "ok"})
    return results


def sync_repo(repo_url, cfg):
    """Sync one repo: clone, detect format, copy skills, clean up.

    Returns a result dict with status, format, and per-category results.
    """
    prefix = cfg["dst_prefix"]
    name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
    clone_dir = TMP_BASE / f"{name}-sync"

    try:
        clone(repo_url, clone_dir)
        fmt, categories, src_base = detect_format(clone_dir, cfg)

        if fmt == "unknown":
            return {
                "source": repo_url, "prefix": prefix, "format": "unknown",
                "status": "unknown_format", "results": [],
            }

        if fmt == "nested":
            results = sync_nested(categories, src_base, prefix)
        elif fmt == "flat":
            results = sync_flat(categories, src_base, prefix)
        elif fmt == "single":
            results = sync_flat([clone_dir.name], clone_dir, prefix)
        else:
            results = []

        total = sum(r["skills"] for r in results)
        return {
            "source": repo_url, "prefix": prefix, "format": fmt,
            "status": "ok", "results": results, "total_skills": total,
        }

    except subprocess.CalledProcessError as e:
        return {
            "source": repo_url, "prefix": prefix, "format": None,
            "status": "clone_fail",
            "error": e.stderr.strip()[:200] if e.stderr else str(e),
            "results": [],
        }
    except Exception as e:
        return {
            "source": repo_url, "prefix": prefix, "format": None,
            "status": "clone_fail", "error": str(e), "results": [],
        }
    finally:
        if clone_dir.exists():
            try:
                rmtree_force(clone_dir)
            except Exception:
                pass


def main():
    load_sources()

    output = {
        "status": "ok",
        "stats": {
            "ok": 0, "clone_fail": 0, "unknown_format": 0,
            "total_skills": 0, "changed": 0,
        },
        "sources": [],
    }

    for repo_url, cfg in REPOS.items():
        result = sync_repo(repo_url, cfg)
        output["sources"].append(result)

        if result["status"] == "ok":
            output["stats"]["ok"] += 1
            output["stats"]["total_skills"] += result.get("total_skills", 0)
            output["stats"]["changed"] += len(result.get("results", []))
        elif result["status"] == "clone_fail":
            output["stats"]["clone_fail"] += 1
        elif result["status"] == "unknown_format":
            output["stats"]["unknown_format"] += 1

    # JSON to stdout for LLM / cron consumer
    print(json.dumps(output, ensure_ascii=False, indent=2))

    # Human-readable summary to stderr (for logs)
    fail_sources = [s for s in output["sources"] if s["status"] == "clone_fail"]
    unknown_sources = [s for s in output["sources"] if s["status"] == "unknown_format"]

    for s in fail_sources:
        print(f"\u274c {s['prefix']}: {s.get('error', 'Unknown error')}", file=sys.stderr)
    for s in unknown_sources:
        print(f"\u26a0\ufe0f {s['prefix']}: 无法识别仓库格式", file=sys.stderr)

    if output["stats"]["changed"] == 0 and output["stats"]["clone_fail"] == 0:
        print("\U0001f504 技能同步 | 无更新", file=sys.stderr)


if __name__ == "__main__":
    main()
