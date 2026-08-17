---
name: music-transcription
description: 扒谱/音频转谱工具评测与使用，含分级实测法与浏览器自动化技巧。触发词：扒谱、音频转谱、音乐转录、和弦提取。
version: 1.0.0
author: hermes
license: MIT
metadata:
  hermes:
    tags: [music, transcription, audio, browser-automation, evaluation]
    related_skills: [song-analysis, songsee, songwriting-and-ai-music]
---

# 音乐转录（扒谱）工具与方法

## When to Use

- 用户要找扒谱工具/项目（在线站、GitHub 开源、模型库），或要评估某个转谱工具的准确度
- 需要把音频转成 MIDI/五线谱/六线谱/和弦谱
- 触发词：扒谱、音频转谱、音乐转录、和弦提取、audio to sheet music、transcription、转谱工具

从音频提取乐谱信息（旋律/和弦/MIDI）的任务。**核心认知：单旋律是全自动的极限，和弦/多声部以上任何工具都要人工修**——这是行业现状，不是某个工具的缺陷。

## 工具生态地图（2026-08 盘点）

| 类别 | 工具 | 定位 |
|---|---|---|
| 纯在线（零安装） | **noteDigger**（madderscientist.github.io/noteDigger/，GitHub madderscientist/noteDigger） | 频谱可视化 + AI 辅助人工扒谱；中文、纯前端、开源；作者 B 站有教程 |
| 纯在线（商业） | Chordify（和弦）、Moises（分轨+和弦）、ScoreCloud（单旋律哼唱转谱） | 流行歌够用，注册门槛 |
| 开源可部署 | **song-to-tab**（linyi012/song-to-tab） | FastAPI+React+Docker Compose；吉他六线谱+五线谱 MusicXML；basic-pitch/librosa 双引擎、和弦、量化、Demucs 人声分离 |
| 模型库 | magenta/mt3（Google）、muscriptor（Kyutai 2026）、sony/hFT-Transformer、basic-pitch（Spotify） | 自建高精度管线用 |

## 实测水平结论（2026-08-14 noteDigger 实测，合成已知音频）

- 纯正弦单旋律：**8/8 全对（100%）**，力度也准
- 带泛音单旋律：主音 8/8 全对 + 2 个弱力度八度谐波误检（velocity≈25 vs 主音 60+，**可按力度阈值过滤**）
- 三和弦进行（C-G-Am-F）：检出 20 音**大量幻觉**（A2/B3/D#3 等非和弦音），根音八度乱（C4 检出成 C2/C3），G 三和弦只出 1 音——**不可用**
- 根因：noteDigger 的 AI 是 basicAMT（Spotify basic-pitch 浏览器移植），单音高估计模型，训练数据以旋律为主
- 作者自称「AI 扒谱准确率 95%」在旋律场景属实，但**只适用于单声部**；工具本质是「频谱可视化+人工扒谱」，AI 只是参考底稿

## 评测方法论：合成 ground truth 分级测试

**不要用真实歌曲评测扒谱工具**（不知道正确答案，无法量化）。合成已知音符的音频，三级难度：
1. 纯正弦单旋律（理想场景，测音高识别上限）
2. 带 2/3 次泛音的单旋律（模拟真实乐器，测去谐波能力）
3. 三和弦进行（多声部，测复调识别）

跑 `scripts/make_test_audio.py` 生成（可传输出目录），工具识别结果转音名序列与真实值对比。MIDI note → 音名：`names[midi%12] + (midi//12 - 1)`。

## 浏览器自动化驱动 web 音频工具（关键技巧）

完整步骤见 `references/noteDigger-browser-automation.md`。要点：
- 现代 web 工具用 `showOpenFilePicker`/动态创建 input，**没有静态 file input**：动态创建 `<input type=file>` 绑定 onchange 调应用内部函数（noteDigger 是 `app.io.onfile(file)`），再用 CDP `DOM.setFileInputFiles` 喂本地文件——比 base64 注入可靠
- **base64 注入 File 对象有 CDP 表达式大小限制**：470KB 直接爆 "Separator is not found, and chunk exceed the limit"（约 100KB 上限）
- **AI 推理会超 evaluate 超时**：`(async()=>{...})()` 改后台跑，结果存 `window.__aiResult`，再轮询读取
- `DOM.setFileInputFiles` 偶发卡死（页面主线程忙于解码/CQT）：**重开 tab + 单独调用 + 给足 timeout**
- **优先找内部 API 绕过 UI**（noteDigger 是 `window.AI.basicamt(AudioBuffer)` 返回音符事件数组）：UI 点击依赖菜单展开/状态，内部函数直取结果更可靠
- 拿音频 PCM：`fetch(audioEl.src /* blob URL */) → arrayBuffer → audioContext.decodeAudioData() → getChannelData(0)`

## 用户协作偏好

- 用户是影视/音乐从业者，评估工具水平**必须实测带证据**，不接受 README/作者自述（"准确率95%"要实测验证）
- 用户环境：gh CLI 可搜 GitHub（`gh search repos` 中文关键词"扒谱"有效）、browser_exec 可驱动真实浏览器
