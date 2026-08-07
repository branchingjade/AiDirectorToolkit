# H3 套件专用同步配置（MiniMax-H3 仓库，2026-08）

完整工作示例：外部 skill 套件**零内容定制**（原名安装 + disabled 名单隔离）时的自动更新方案。

## 背景

- 仓库：https://github.com/MiniMax-AI/MiniMax-H3（自带 9 个 skills，位于 `skills/<name>/SKILL.md`；其中 **h3-prompt-writing 已本地定制退出同步**，见下节）
- 隔离方式：剩余 8 个 skill 全部 `config.yaml skills.disabled` 硬禁用（全路径硬门禁：不进系统提示、skill_view 拒绝、/skill 按 missing）
- **零内容定制**：目录名 = 仓库原名、frontmatter name = 仓库原名、description 原文不动、不删 trigger-words
- 唤醒：通用 `external-skill-access` 指路牌（read_file 直读磁盘，不依赖记忆）
- 为什么不需要定制：disabled 把技能从系统提示里整个移除，模型看不到名字/描述，内容级门禁全部冗余（极限测试证明：disabled 失效时任何内容门禁都防不住名字命中，所以定制是无效成本）

## 同步脚本（sync-h3-skills.py，位于 ~/AppData/Local/hermes/scripts/）

核心逻辑（简化版）：

```python
SKILL_NAMES = [  # 仓库目录名 = 本地目录名
    "h3-prompt-writing", "3d-animation-short-generator", "brand-promo-video-generator",
    "co-op-game-intro-generator", "handdrawn-live-video-generator",
    "minimalist-product-ad-generator", "mv-subtitle-skill-confirmed",
    "paper-collage-explainer-generator", "papercraft-stop-motion-explainer",
]
FM_NAMES = {  # 目录名 ≠ frontmatter name 的特例（disabled 按 frontmatter name 匹配）
    "mv-subtitle-skill-confirmed": "music-video-subtitle-generator",
}

def ensure_disabled():
    """幂等地把 9 个名字（含 FM_NAMES 的 frontmatter name）写进 skills.disabled。"""
```

流程：clone → 按原名复制到 skills/ 根目录 → ensure_disabled。**没有重命名、没有门禁、没有 trigger 清理**。

## h3-prompt-writing 本地定制（2026-08-07，退出同步）

用户拍板：H3 提示词**默认输出中文**（正文中文，字段名/结构标签/对白原语言保留英文）。改动落在 SKILL.md Output Rules + references/base-en.txt + references/ref-en.txt 全部示例正文。

- 已从 `sync-h3-skills.py` 的 `SKILL_NAMES` 移除（**否则 cron 同步 `rmtree_force` + `copytree` 会把本地中文版整个删掉换回英文**）
- 仍留在 config.yaml `skills.disabled`（幂等并集，不会因移出名单而启用）
- 上游 MiniMax-H3 更新 h3-prompt-writing 时需手动比对合并，不再自动同步

关键点：disabled 名单写 **frontmatter name**（不是目录名）——`mv-subtitle-skill-confirmed` 目录的 frontmatter name 是 `music-video-subtitle-generator`，两个都要处理。

## 验证方法

```bash
cd ~/AppData/Local/hermes/scripts && python sync-h3-skills.py
hermes skills list  # 8 个 skill 全部显示 disabled（h3-prompt-writing 已退出同步，见下）
```

程序化验证：
- 9 个目录名 == 仓库原名
- frontmatter name == 仓库原名（mv-subtitle 特例为 music-video-subtitle-generator）
- description 无门禁前缀
- config.yaml skills.disabled == 9 个原名（frontmatter name）
- 幂等：重复运行结果一致

## Cron 并入（不新建 job）

现有「外部技能同步」cron（job e14576c54fcf，0 9 * * *，LLM 驱动）prompt 追加：

```
2. 用 terminal 执行：python3 ~/AppData/Local/hermes/scripts/sync-h3-skills.py
   （H3 套件专用同步——原名复制 + 确保 disabled；与通用同步分离，不要改动脚本）
```

## 陷阱

- disabled 匹配的是 **frontmatter name**，不是目录名（mv-subtitle 特例实测）
- 临时 clone 目录放 ~/Documents/Hermes/ 下（MSYS /tmp 与 git 路径不一致会 clone 失败）
- cron prompt 更新用 cronjob(action='update')，不要动 jobs.json（网关保护）
- gateway 重启可能重写 config.yaml 清掉 skills.disabled——发现技能变 enabled 就重新应用名单（或走 hermes skills config 受控路径）
