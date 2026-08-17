# noteDigger 浏览器自动化实测全记录（2026-08-14）

对 https://madderscientist.github.io/noteDigger/ 的完整驱动方法 + 实测结果。方法可迁移到其他纯前端 web 音频工具。

## 页面内部结构（实测探明的 API）

- `window.app` 主应用对象：
  - `app.io.onfile(file)` — 音频导入入口（input 的 onchange 调它）
  - `app.io.projFile(file)` / `app.io.midiFile(file)` — 项目/MIDI 导入
  - `app.AudioPlayer.audio` — HTMLAudioElement，`src` 是 blob URL
  - `app.audioContext` — AudioContext（decodeAudioData 可用）
  - `app.MidiAction.midi` — 音符数据（人工绘制的）
  - `app.Analyser` — `basicamt / septimbre / beatEst / reduceHarmonic / autoNoteAlign`（菜单项背后的方法）
- `window.AI` — 扒谱引擎入口：
  - `AI.basicamt(audioBuffer)` → Promise<音符事件数组>（basicAMT，本地 Web Worker，无需网络）
  - `AI.combineChannels(audioChannel)` — 入参需是 **AudioBuffer**（有 getChannelData），不是裸 Float32Array
  - 事件格式: `{onset, offset, note /*MIDI*/, velocity}`
- 上传弹框按钮：「解析」（点它才跑 CQT 频谱分析）；选项有 CQT/GPU/声道
- 分析菜单项：调性分析 / 节奏分析 / 自动节奏型 / 去除谐波 / 和弦分析 / 数字谱对齐音频 / 人工智障扒谱 / 音色分离扒谱
- 调性分析结果只画在频谱 canvas 上，不暴露全局数据——无法自动化读取

## 驱动流程（每步独立 browser_exec 调用）

1. `new_tab(url)` + `wait_for_load()`
2. 动态建 input 并绑 onchange：
   ```js
   const i = document.createElement('input');
   i.type = 'file'; i.id = '__fup'; i.style.display = 'none';
   i.onchange = () => { window.app.io.onfile(i.files[0]); };
   document.body.appendChild(i);
   ```
3. CDP 上传本地文件（触发 change → onfile → 弹分析选项框）：
   ```python
   doc = cdp('DOM.getDocument', depth=1)
   q = cdp('DOM.querySelector', nodeId=doc['root']['nodeId'], selector='#__fup')
   cdp('DOM.setFileInputFiles', nodeId=q['nodeId'], files=['C:\\path\\to\\test.wav'])
   ```
4. 点「解析」→ sleep 6s 等 CQT 算完
5. 后台跑 AI 扒谱（**不能 await**，推理会超 evaluate 超时）：
   ```js
   window.__aiResult = 'RUNNING';
   (async () => {
     const src = window.app.AudioPlayer.audio.src;              // blob URL
     const buf = await (await fetch(src)).arrayBuffer();
     const ab = await window.app.audioContext.decodeAudioData(buf.slice(0));
     const events = await window.AI.basicamt(ab);               // AudioBuffer 入参
     window.__aiResult = JSON.stringify(events || []);
   })();
   ```
6. 轮询 `window.__aiResult`（10s 间隔，模型 worker 首次加载约 10-30s）

## 踩过的坑

| 坑 | 现象 | 解法 |
|---|---|---|
| 无静态 file input | `querySelector('input[type=file]')` 返回空 | 动态创建 input（见上）；页面自身用 `showOpenFilePicker` + 动态 input |
| base64 注入超限 | 470KB base64 字符串 → "Separator is not found, and chunk exceed the limit" | CDP `Runtime.evaluate` 表达式约 100KB 上限；改用 `DOM.setFileInputFiles` 本地路径 |
| AI 推理超时 | `(async()=>{...})()` 直接 evaluate 超时（30s+） | 后台启动存全局变量 + 轮询 |
| setFileInputFiles 卡死 | CDP IPC timeout（页面主线程忙） | 重开 tab、该调用单独发、timeout 给 300s；成功后再 sleep 10s 才读页面 |
| 入参类型错 | "audioChannel.getChannelData is not a function" | `AI.basicamt` 要 AudioBuffer 不是 Float32Array |
| MSYS 路径坑（本机 bash） | `/c/Users/...` 被 Windows Python 转成 `C:\c\Users\...` | 传 Windows 盘符路径 `C:/Users/...`；脚本内路径用反斜杠转义 |

## 实测结果（合成 ground truth）

| 测试 | 真实值 | 结果 |
|---|---|---|
| scale_pure（纯正弦音阶） | C4 D4 E4 F4 G4 A4 B4 C5 | **8/8 全对**，velocity 也准 |
| scale_harmonic（带泛音） | 同上 | 8/8 主音对 + 2 误检 G5/A5（2次谐波，vel≈25 vs 主音 58-69，按力度过滤） |
| chords（C-G-Am-F） | 12 音 | 20 检出音大量幻觉（A2/B3/D#3/F2 非和弦音），根音八度乱，G 三和弦只出 1 音 → 不可用 |

时间戳单位：帧（basicAMT 22050Hz hop=256 → 1 帧 ≈ 11.6ms）。

## 结论

- AI 扒谱（basicAMT）只适合单声部旋律线（人声/主音）；和弦/多声部给幻觉
- noteDigger 正确定位 = 频谱可视化 + 人工扒谱辅助（调性/节奏/谐波分析帮助人工），不是全自动出谱工具
