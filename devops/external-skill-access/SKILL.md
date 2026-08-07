---
name: external-skill-access
description: "Use when user mentions a disabled skill needing content."
version: 1.0.0
author: agent
platforms: [windows, linux, macos]
---

# External Skill Access — 被禁用技能的通用唤醒指路牌

**唯一用途**：用户明确提到某个被 `config.yaml skills.disabled` 硬禁用的技能（如 H3 套件、或未来任何被禁用的外部技能），需要用到它的内容时，用 `read_file` 直接读取该技能的磁盘文件进入当前会话。

## 背景

disabled 是**全路径硬门禁**：被禁技能不进系统提示（自动触发不可能）、`skill_view` 工具拒绝（报 "Skill is disabled"）、`/skill` 指令按 missing 处理。**但 `read_file` 不检查 disabled**——技能文件完整躺在磁盘上，直接读就能用。本 skill 就是这条唯一合法通道的常驻指路牌，替代易失的记忆作为唤醒线索（记忆被清理后依然可用）。

本 skill 是通用的：不绑定任何具体技能。凡被禁用的技能套件，都走同一模式——用户提到它 → 本 skill 触发 → read_file 读磁盘 → 内容进会话 → 会话结束即弃。

## 通用流程

1. 用户提到被禁用的技能名/套件（如 "H3"、"minimax"、"海螺" 等）并需要其内容
2. 用 `read_file` 读取：
   - 主规范：`C:\Users\HMSJ\AppData\Local\hermes\skills\<技能目录>\SKILL.md`
   - 按需读取同目录 `references\*`、`templates\*` 等支持文件
3. 按读到的规范干活
4. 会话结束即弃——不持久化、不启用、不改配置

## 已知案例：H3 套件（9 个技能，2026-08）

来源 MiniMax-AI/MiniMax-H3 仓库，全部被 disabled（仓库原名，无任何本地内容定制——隔离只靠 disabled 名单）：

- 核心：`h3-prompt-writing`（H3 三段式提示词：`integrated_multimodal_description` 画面 + `overall_soundscape` 音效 + `non_diegetic_music` 配乐；Ref2VA 六段式含 subject_definitions/summary/retention_analysis）
- 规范文件：`references\base-en.txt`（T2VA/I2VA/FL2VA/L2VA）、`references\ref-en.txt`（Ref2VA）
- 其余 8 个风格化生成器（3d-animation / brand-promo / co-op-game / handdrawn / minimalist-product-ad / music-video-subtitle / paper-collage / papercraft-stop-motion）——MiniMax Hub 生态专属，Hermes 环境触发会卡，仅参考

## 规则

- 不修改 config.yaml 的 `skills.disabled`——保持全禁用
- 不用 `skill_view` 工具（会被 disabled 拒绝），一律 `read_file`
- 会话结束即弃——不持久化、不启用
- 用户没提到被禁技能时，本 skill 不参与任何触发
