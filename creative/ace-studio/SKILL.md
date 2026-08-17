---
name: ace-studio
description: "ACE Studio AI音乐工作站 — 通过MCP控制AI人声合成、乐器演奏、混音编排的完整知识库。"
version: 1.0.0
author: agent
license: MIT
metadata:
  hermes:
    tags: [music, audio, ai-vocal, mcp, ace-studio]
---

# ACE Studio — AI 音乐工作站

ACE Studio 2.0 是一个 AI 驱动的音乐工作站，核心理念：MIDI + 歌词 → AI 人声，MIDI → AI 乐器演奏。

## Suno → ACE Studio 提示词转换（2026-08-13 实战）

用户把 Suno Style 换成 ACE Studio 提示词时，先说明差异：**ACE 没有 Style 字段**，两条路径：

1. **Inspire Me（最接近 Style 的输入）**：把 Suno Style 翻译成完整歌曲描述——风格流派 + BPM + 调性 + 拍号 + 人声类型 + 逐段落情绪轨迹（含每段的乐器/力度/人声状态）+ 乐器清单。中文描述即可，ACE 界面中文。
2. **手动工程参数**（Inspire Me 结果不理想时按这个搭）：
   | 项目 | 参数 |
   |---|---|
   | Transport | BPM、拍号（双击输精确值） |
   | Chord Track | 全曲和弦进行（含副歌属和弦、间奏半音下行） |
   | 人声轨 | 选支持中文的声库；Vocal Controls：主歌 Soft/Breathy 拉高、副歌 Power 拉满 |
   | 乐器轨 | 按段落分配（钢琴主歌主导 → 弦乐 pad 预副歌 → 失真吉他/铜管/合唱副歌 → 鼓预副歌起） |
   | 歌词 | 每音符一音节，长音 `-` 连字符 melisma |

## ⚠️ .drp 扩展名鉴别陷阱（2026-08-13 实测）

`.drp` 不一定是 ACE Studio 工程——**DaVinci Resolve 工程也是 .drp**。鉴别：unzip 后看 project.xml 头——`DbAppVer` / `SM_Project` / `FieldsBlob` / `MediaPool` / `SeqContainer` = 达芬奇工程（达芬奇 Studio 21 格式）；ACE Studio 工程结构不同。用户发来 .drp 时先解压鉴别再按对应格式解析（达芬奇工程：工程名/时间线片段数可从 project.xml 与 SeqContainer/<uuid>.xml 提取，素材文件名在 FieldsBlob 二进制里，无明文路径；剧本文本/歌词不在此类文件中）。

## MCP 连接（已配置）

Windows STDIO 模式，已在 Hermes config.yaml 中配置：

```yaml
mcp_servers:
  ace-studio:
    command: "C:/Program Files/ACE Studio/ace_mcp_server.exe"
    args: ["--stdio"]
```

前置条件：`pip install mcp`。重启 Hermes 后工具以 `mcp_ace_studio_*` 前缀注册。
ACE Studio 客户端需运行中。MCP Server 在 Preferences → General → MCP Server 中设为 STDIO 模式。

## 工程结构

**Canvas → Track → Clip → Clip Editor**

- Canvas：编排主界面，每行一条轨道
- 轨道：MIDI 轨（挂 AI 人声/乐器）或音频轨
- Clip：内容基本单位，可拖拽调长度、切割（Ctrl+E）、淡入淡出
- Clip Editor：双击 Clip 打开——人声/乐器进钢琴卷帘，音频进音频编辑器

## AI 人声创作流程

选声音 → 挂 MIDI 轨 → 建 Clip → 填音符+歌词 → 调音高+控制参数

### 声音来源
- 预置声音（官方训练，多数免版税）
- 克隆声音（上传样本克隆）
- 社区声音（其他用户发布）
- 融合声音（多声音种子按比例混合，Blending）
- 齐唱模式（Unison，多声音叠加同一轨，调 Offset/Spread/Gain）

### 音符编辑（钢琴卷帘）
- V 键 Note Mover：双击创建、拖拽移动、拉边缘调长度
- B 键 Note Brush：拖动画音符
- X 键 Note Slicer：切割音符（做花腔 melisma）
- 人声轨单音限制（monophonic），重叠自动裁剪
- 最长音符：Verse25 <20s，旧模型 <18s
- 网格吸附支持三连音（选 3 Cell/Beat）

### 歌词系统
- 每个音符一个音节
- `-`（连字符）= melisma（前一音节跨多个音符）
- 三种编辑：逐行输入（自动拆分音节）、双击音符、歌词面板（Ctrl+E）
- 每个音符有语言属性，不匹配有红色警告

### 音高编辑（6 工具）
- Pitch Brush（1）：自由画曲线
- Pitch Anchor：锚点式画线
- Fixed Brush（2）：锁定 AI 音高某部分
- Pitch Eraser（3）：擦除用户音高
- Vibrato（4）：拖动画颤音（振幅/频率/相位/包络）
- Modulation（5）：控制音高动态范围
- AI Pitch（深色，自动）vs User Pitch（白色，手绘覆盖）

### Vocal Controls（Verse25+）
- 基础四维：Power / Soft / Breathy / Chest
- 特殊控制（特定声音）：Rap / Opera / Chinese Opera
- 无手动编辑时 AI 自动推断
- 还有 Breath（气息）面板：手动添加或 "Add all" 自动放置

### 演唱语言
- 每个 AI 声音多语言支持，有母语
- 轨道默认语言可设置
- 每个音符可单独设语言属性
- 改语言后需手动改对应歌词

## AI 乐器创作流程

选乐器 → 挂 MIDI 轨 → 建 Clip → 填音符 → 演奏技法+表情

### 演奏技法（Articulations）
- Smart（默认，AI 自动选）
- General / Legato / Glissando / Pizzicato / Tremolo / Growl / Scoop / Arp-fall
- 可用技法因乐器而异

### 表情控制（Expression Controls）
- Vibrato：时间线上画颤音区域
- Split-tones：多音同时发声
- 右键拖拽擦除

## 编排

### Transport
- 速度 1-360 BPM，双击输入精确值
- 播放：空格 | 从头：Enter | 继续：Shift+空格
- 节拍器、循环模式（Ctrl+L）、自动滚动

### Chord Track
- 全局和弦轨，固定最上方
- 双击创建和弦片段，编辑根音+和弦性质+低音
- 支持循环
- 可作钢琴卷帘背景（Scale Mode 切为 Chord）

## 混音

- Mixer（M 键）：每条轨+Master，推子/声像/独奏/静音/FX
- FX 链：串行处理，内置效果器 + VST3/AU 第三方插件
- 效果器芯片：蓝=激活，黄=旁通，灰=停用
- Room Effect：人声轨空间定位

## AI 工具（10 个）

| 工具 | 功能 |
|------|------|
| Inspire Me | 文字描述/歌词 → 生成完整歌曲 |
| Add a Layer | 选类型+风格描述 → 生成匹配新层 |
| Music Enhancer | 选中区域 → AI 重新演绎 |
| Vocal to MIDI | 人声音频 → MIDI+歌词 |
| Voice Changer | 人声 → 其他人声/乐器音色 |
| Stem Splitter | 分离混音轨 |
| Doubles | 叠层加宽加厚 |
| Sound Effects | 生成音效 |
| Video Composer | 视频配乐 |
| MCP Server | 外部 AI 控制 |

## 其他

- 导入：MIDI、MusicXML、音频
- 导出：音频/MIDI/工程文件
- 渲染：云端或本地
- ACE Bridge 2：VST3/AU 插件接入 DAW
- Voice Cloning：克隆人声（可用于 Vocal Synth 或 Voice Changer）

## 官方文档

- 主页：https://docs.acestudio.ai
- MCP Server：https://docs.acestudio.ai/ai-tools/ace-studio-mcp-server
- llms.txt：https://docs.acestudio.ai/llms.txt
- 任意页面加 `.md` 后缀获取 Markdown 版本
