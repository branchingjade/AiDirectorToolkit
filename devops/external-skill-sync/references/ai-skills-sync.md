# AI-Skills (branchingjade) 同步实现

## 仓库信息

- URL: `https://github.com/branchingjade/AI-Skills.git`
- 格式: **已变更** — 当前为 single 格式（根目录直接放置 `.md` 文件），不再是 `.skill` ZIP
- 目标目录: `$SKILLS_DST/ai-skills/`
- 配置方式: 通过 `hermes_skill_sources.yaml` 声明（prefix: `ai-skills`）

## 已知技能（截至 2026-07 同步）

- AI短剧导演助手（`AI短剧导演助手.md`）
- AI提示词助手（`AI提示词助手.md`）
- AI短剧编剧助手（`AI短剧编剧助手.md`）

## 同步方式

脚本 `detect_format()` 自动判定为 `single` 格式（克隆目录根有 `.md` 文件），走 `sync_flat()` 路径。每个 `.md` 文件被当作一个独立技能复制到 `ai-skills/` 下。无需手动维护同步函数。

## 注意事项

- 仓库格式历史上是 `.skill` ZIP，现已变为直接的 `.md` 文件，未来可能再次变化
- 如果未来恢复为 `.skill` ZIP 格式，需在 `detect_format` 中添加 ZIP 检测分支（检查 `clone_dir.glob("*.skill")`）
- 中文文件名在 Windows 的 `zipfile` 中需额外处理 cp437 编码

## .skill ZIP 格式（历史参考，当前不使用）

如果未来仓库恢复为 `.skill` 格式，同步逻辑参考：

```python
import zipfile

def sync_zip_skills(clone_dir):
    dst_base = SKILLS_DST / "ai-skills"
    dst_base.mkdir(parents=True, exist_ok=True)
    results = []
    for skill_file in clone_dir.glob("*.skill"):
        skill_name = skill_file.stem
        dst = dst_base / skill_name
        dst.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(skill_file, 'r') as zf:
            zf.extractall(dst)
        results.append({"category": skill_name, "skills": 1, "status": "ok"})
    return results
```

`.skill` 文件本质是 ZIP 压缩包，内含 `SKILL.md`（可能还包括 references/、templates/ 等）。解压后需确认 SKILL.md 存在才视为有效同步。
