# DaVinci Resolve 性能排障

快速诊断 Resolve 卡顿/丢帧/播放不流畅的完整流程。按优先级排列。

## 诊断步骤（按顺序执行）

### 1. GPU 显存分析

```bash
# 查看 GPU 型号、驱动版本、显存使用
nvidia-smi --query-gpu=name,driver_version,memory.total,memory.used,memory.free --format=csv,noheader
```

**阈值：**
- RTX 5060 Ti (8GB)：4K 时间线最低需要 4-6GB 空闲显存
- 后台应用常驻消耗 2-3GB → 留给 Resolve 的只有 5-6GB → **临界状态**

### 2. 后台 GPU 进程排查

```bash
# 列出所有占用 GPU 的进程
nvidia-smi --query-compute-apps=name,used_memory --format=csv,noheader
```

**常见显存大户（需在开 Resolve 前关闭）：**
| 进程 | 典型占用 | 操作 |
|------|:--:|------|
| Wallpaper Engine | ~400MB | 暂停或退出 |
| Chrome/Edge（多标签） | 300-500MB | 关闭 |
| Steam WebHelper | ~200MB | 退出 Steam |
| Eagle | ~200MB | 关闭 |
| 飞书/豆包 | ~150MB | 可不关 |
| 网易云音乐 | ~100MB | 关闭 |

### 3. 驱动类型检查

```bash
nvidia-smi --query-gpu=driver_version --format=csv,noheader
```

**Game Ready vs Studio：**
- Game Ready 驱动（如 610.62）针对游戏优化，Resolve 稳定性不如 Studio 驱动
- **Resolve 强烈推荐 NVIDIA Studio Driver**
- 换驱动后通常立竿见影

### 4. Resolve 内快速优化（不需 MCP）

| 操作 | 路径 | 效果 |
|------|------|------|
| 代理模式 | Playback → Proxy Mode → Half Resolution | 显存压力减半 |
| 渲染缓存格式 | Project Settings → Master Settings → Optimized Media Format → DNxHR LB | 压缩缓存，减少磁盘+显存占用 |
| 降低播放分辨率 | Playback → Timeline Proxy Resolution → Half | 播放时降分辨率 |
| Fusion 内存缓存 | Playback → Fusion Memory Cache → 关闭或降低 | Fusion 合成时释放显存 |

### 5. Resolve 配置检查

配置文件位置：`%APPDATA%\Blackmagic Design\DaVinci Resolve\Preferences\config.user.xml`

关注项：
```xml
<AutoSaveMode>1</AutoSaveMode>       <!-- 1=定时备份 -->
<AutoSaveDuration>5</AutoSaveDuration> <!-- 每5分钟 → 到点会微卡 -->
<PerfModeType>PERF_MODE_AUTOMATIC</PerfModeType>  <!-- 自动性能模式 -->
<FusionMemoryCacheMode>FUSION_MEMORY_CACHE_MODE_AUTO</FusionMemoryCacheMode>
```

### 6. 笔记本特别注意事项

- **散热降频**：i7-13650HX + RTX 5060 Ti 长时间满载会触发 thermal throttling
- **电源模式**：必须插电 + Windows 电源计划设"高性能"
- **NVIDIA 控制面板**：Resolve 设"首选最大性能"

## 硬件基线

| 分辨率 | 最低 VRAM | 推荐 VRAM |
|--------|:--:|:--:|
| 1080p | 4GB | 6GB |
| 4K (无 Fusion) | 6GB | 8GB+ |
| 4K + Fusion/降噪 | 8GB | 12GB+ |
| 8K | 12GB | 24GB+ |

## 常见误区

- ❌ "关掉 Resolve 再开就不卡了" → VRAM 碎片化不一定释放，需重启电脑
- ❌ "MCP 工具导致 Resolve 卡" → MCP 是独立进程，不消耗 Resolve 的 GPU 资源
- ❌ "缓存越多越快" → 缓存盘满了反而变慢，定期清理 `AutoCacheDeleteMode`
