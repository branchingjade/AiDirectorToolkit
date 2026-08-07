# 外部 skill 干扰防护——极限测试实录（2026-08-06）

场景：安装 MiniMax-H3 仓库 9 个影视生成 skill 后，用户要求"只有明确提到 minimax/h3 才触发"，
不能干扰用户自有 skill（AI提示词助手是 Seedance 2.0 提示词主本）。

## 测试方法

用 `hermes chat -q "忽略任务本身，只回答：面对这个请求你会加载哪些skill？请求：<用例>" --source stress-test`
开**真实新会话**验证（配置改动对已有会话不生效）。18 个用例：15 个对抗（旧触发词 + 影视日常）+ 3 个正向（H3/minimax/Ref2VA）。

## 三轮结果

### 第一轮：description 门禁（软）
- 改动：9 个 SKILL.md 的 description 开头加
  `ONLY use this skill when the user explicitly mentions MiniMax H3 (...)`
- 结果：10+ 对抗用例误触发 ❌
- 根因：① 模型靠 **skill 名字**命中（"paper-collage-explainer-generator 直接命中！"）；
  ② 系统提示里 description 被截断到 **57 字符**，模型看到的是
  `ONLY use this skill when the user explicitly mentions MiniMax H3 (minimax, h3,...`
  "Do NOT trigger on generic requests" 后半句根本没进上下文。

### 第二轮：重命名加 h3- 前缀 + 门禁压缩到 57 字符内
- 改动：目录名/frontmatter name 全部加 `h3-` 前缀；
  门禁压成 `H3-only. Trigger only on explicit H3/MiniMax mention.`（55 字符，窗口内可见）
- 结果：12 个对抗用例仍误触发 ❌（比第一轮还差——测试方差）
- 根因：前缀挡不住名字主体泛词段（`h3-music-video-subtitle-generator` 仍含 music-video，
  `h3-paper-collage-...` 仍含 paper-collage），模型照靠名字段命中。

### 第三轮：config.yaml skills.disabled 硬禁用 ✅
- 改动：`config.yaml` 的 `skills.disabled` 数组加入 9 个注册名
- 结果：15/15 对抗用例零误触发，3/3 正向用例正确指向 h3-prompt-writing
- 机制：禁用的 skill 从系统提示的可用列表里**整个消失**（`agent/prompt_builder.py`
  `disabled` 集合在注入前过滤），模型看不到名字 = 零误触发可能。

## 关键机制细节

- **57 字符截断**：系统提示 available_skills 列表里每个 skill 的 description 截断到
  57 字符 + "..."。门禁文本必须在前 57 字符内传达完整禁令，否则等于没有。
- **注册名 vs 目录名**：disabled 列表匹配 frontmatter `name` 字段（如
  `music-video-subtitle-generator`），不是目录名 `mv-subtitle-skill-confirmed`。
- **disabled 不挡手动加载**：`/skill <name>` 仍然可用——这是"特定场景才用"的正确语义。
- **config.yaml 重写注意**：用 yaml.safe_dump 重写 config.yaml 会丢注释（本次文件原本
  无注释无损失），有注释的配置应用 `hermes config set` 或手动 patch 而非全量 dump；
  改前确认有 .bak 备份。
- **YAML 块标量陷阱**：给 `description: |`（块标量）加前缀时不能拼成 `description: GATE |`——
  `|` 必须独占 description 行。应把门禁作为块内第一行（缩进）。单行 description 则直接拼。

## 结论

描述级门禁（软）在名字泛词面前防不住——模型靠名字命中，不看完整描述。
**只有系统提示级移除（hard disable）才是真门禁**。需要"仅特定语境触发"的外部 skill，
一律用 `skills.disabled`，不要试图用 description 文本控制。
