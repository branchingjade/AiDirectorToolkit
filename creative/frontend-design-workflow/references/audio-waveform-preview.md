# 音频波形预览组件（Eagle 风格）

> 场景：列表/历史里给音频条目做波形预览，替代原生 `<audio controls>`（丑、占高、不可定制）。Eagle 素材库的音频预览即此形态：静态波形条 + 播放控制 + 点击跳转。

## 实现要点（纯前端，零后端）

```js
// 1. 峰值解码：Web Audio decodeAudioData 取 N 点峰值（本工作区用 240）
const peaksCache = new Map();           // url -> Float32Array，同 URL 只解码一次
let audioCtx = null;
function ctx(){ if(!audioCtx) audioCtx = new (window.AudioContext||window.webkitAudioContext)(); return audioCtx; }
async function loadPeaks(url){
  if(peaksCache.has(url)) return peaksCache.get(url);
  const buf = await (await fetch(url)).arrayBuffer();
  const data = await ctx().decodeAudioData(buf);
  const ch = data.getChannelData(0);
  const block = Math.floor(ch.length / PEAKS);
  const out = new Float32Array(PEAKS);
  for(let i=0;i<PEAKS;i++){ let max=0; const s=i*block;
    for(let j=0;j<block;j++){ const v=Math.abs(ch[s+j]); if(v>max) max=v; }
    out[i]=Math.min(1, max*1.6);        // 1.6 增益让低响度波形可见
  }
  peaksCache.set(url, out); return out;
}

// 2. 绘制：canvas 竖条（2x DPR 高清），进度前白色 .9 / 后 .25
function draw(cv, peaks, progress){
  const g = cv.getContext('2d'); g.clearRect(0,0,cv.width,cv.height);
  const barW = cv.width/peaks.length, mid = cv.height/2;
  for(let i=0;i<peaks.length;i++){
    const bh = Math.max(1, peaks[i]*(cv.height-6));
    g.fillStyle = (i/peaks.length <= progress) ? 'rgba(255,255,255,.9)' : 'rgba(255,255,255,.25)';
    g.fillRect(i*barW+0.5, mid-bh/2, Math.max(1,barW-1), bh);
  }
}
```

## 交互与性能铁律

- **懒解码**：IntersectionObserver（rootMargin 80px）可见才 `fetch+decode`，避免列表一次性拉全部音频（流量大头）。占位期 `loading` 半透明
- **播放**：容器内藏 `<audio preload="none">`；▶ 按钮 `togglePlay`；播放中 rAF 按 `currentTime/duration` 重绘进度（`ended`/`pause` 时停 rAF 收尾）
- **seek**：点波形任意位置 → `currentTime = ratio * duration` 并播放（`clientX - rect.left` 算比例）
- **事件**：波形容器 click 必须 `stopPropagation`——它在行内，会误触父级行的展开/选中
- **缓存**：峰值 Map + 单 AudioContext（浏览器限制多 context）
- **渲染集成**：模板输出 `<div class="wave" data-url data-dur>` 空容器，渲染完成后 `WaveEngine.init(container)` 统一扫描初始化（防 innerHTML 重复注入）

## 参考

- Web Audio API：developer.mozilla.org/docs/Web/API/Web_Audio_API（decodeAudioData 支持 wav/mp3/ogg，浏览器自带解码，无需后端 ffmpeg）
- 完整实现：doubao-tts-server `app/page.html` 的 `WaveEngine`（2026-08-10 实测通过）
