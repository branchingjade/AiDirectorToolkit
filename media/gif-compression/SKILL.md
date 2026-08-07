---
name: gif-compression
description: 压缩GIF动图到指定分辨率/体积，含远程文件获取回写。触发词：压缩gif、gif太大、动图压缩、gif优化。
---

# GIF 动画压缩与文件获取

## 触发条件
用户要求压缩 GIF（限体积/分辨率）、优化动图、或从远程位置（NAS/网络盘）取回/写回文件。

## 第一步：诊断（先看再动）
```python
from PIL import Image
im = Image.open(path)
print("帧数:", im.n_frames, "尺寸:", im.size, "模式:", im.mode)
durations = [im.seek(i) or im.info.get('duration', 40) for i in range(im.n_frames)]
```
关键参数：帧数、总时长、是否无限循环（loop=0）、每帧 duration（0ms 帧按 10ms 计）、内容类型（照片级真人 → LZW 压缩率差，需激进降帧；卡通/扁平色 → 压缩率高）。

## 压缩杠杆（按性价比排序）
1. **分辨率缩放**：面积缩 1/4，体积通常降 50%+。`resize((w,h), Image.LANCZOS)`。
2. **抽帧**：均匀采样 N 帧 `idx = sorted(set(round(i*(n-1)/(N-1)) for i in range(N)))`，每帧 duration = 总时长/N。25fps→12.5fps 体积约降 15-25%，画质无感。
3. **抖动开关**：FLOYDSTEINBERG 保留渐变质感但增体积；`Image.Dither.NONE` 出纯色块/色带但体积小。
4. **色数**：256→128 对复杂内容（真人视频）收益很小，先别指望降色。
5. **gifsicle 二次优化**：`--optimize=3` 通常再省 5-15%（对已 optimize 的 PIL 输出仍有效）。
6. **每帧独立调色板 vs 共享调色板**：共享板（首帧/采样帧 MEDIANCUT）体积小但色彩受限；内容色彩多变时质量受损。

## 核心坑（PIL 调色板——颜色偏灰的根因）
**❌ 错误**（颜色全部错乱偏灰）：
```python
pf = fr.convert('P')        # 每帧独立自适应量化，生成自己的索引
pf.putpalette(shared_pal)   # 强行换调色板 → 索引对应错位 → 色彩偏灰偏冷
```
**✅ 正确**（索引正确映射到共享调色板）：
```python
pal = rgb_frames[0].quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)  # P模式共享板
pf = fr.quantize(palette=pal, dither=Image.Dither.FLOYDSTEINBERG)  # 逐帧映射到共享板
```
**dither 参数**：必须传 `Image.Dither.NONE` 枚举；`dither=None` 会被当默认（抖动仍生效），测试结果看似没变就是没生效。

## 完整压缩流程（已验证）
```python
from PIL import Image
import os, subprocess

def compress_gif(src, out, target_size, target_fps=None, colors=256,
                 palette_source='first', gifsicle=None):
    im = Image.open(src)
    n = im.n_frames
    durs, frames = [], []
    for i in range(n):
        im.seek(i)
        durs.append(im.info.get('duration', 40))
        frames.append(im.convert('RGB').resize(target_size, Image.LANCZOS))
    total_ms = sum(max(d, 10) for d in durs)
    # 抽帧（均匀采样，保留首尾）
    if target_fps:
        nf = max(2, round(target_fps * total_ms / 1000))
        idx = sorted(set(round(i * (n - 1) / (nf - 1)) for i in range(nf)))
        frames = [frames[i] for i in idx]
    d = [round(total_ms / len(frames))] * len(frames)
    # 调色板（首帧即可；全帧采样更均衡但体积明显更大）
    pal = frames[0].quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    p = [f.quantize(palette=pal, dither=Image.Dither.FLOYDSTEINBERG) for f in frames]
    p[0].save(out, save_all=True, append_images=p[1:], duration=d, loop=0, optimize=True)
    if gifsicle and os.path.exists(gifsicle):
        gs = out.replace('.gif', '_gs.gif')
        subprocess.run([gifsicle, '--optimize=3', '-o', gs, out], check=True, capture_output=True)
        out = gs
    return out
```
**体积预估**：照片级真人 GIF（噪声大）110帧@25fps@706×992 ≈ 17MB；压到 353×496 后，5MB 内通常只能到 12-15fps（55-68帧）。别承诺"全帧率+小体积"——GIF 格式物理上限。

## gifsicle（Windows 可用）
- 下载：`curl -L -o gs.zip https://eternallybored.org/misc/gifsicle/releases/gifsicle-1.95-win64.zip`，解压取 gifsicle.exe
- 命令：`gifsicle --optimize=3 --colors 256 -o out.gif in.gif`（可叠加 `--resize WxH`）
- `--fps` 参数不存在（gifsicle 不支持按 fps 抽帧），抽帧必须先用 PIL
- 压缩率对比：PIL optimize=True 后 gifsicle 仍可再省 5-15%

## WebP 动画（备选，兼容性受限）
同样内容 WebP 动图体积约为 GIF 的 1/4-1/3，可全帧率保流畅。但 Eagle/部分平台不支持 WebP 动图播放，**先确认目标平台兼容性再选**。

## 文件获取（本地/网络盘/NAS 通用排查）
1. **直接可用**：本地路径 → 直接用。
2. **盘符不存在/不可见**（网络盘未映射、UAC 隔离、服务会话）：
   - 排查：`Get-PSDrive`、`net use`、`subst`、`Get-SmbMapping`（当前进程权限下）
   - 提升/非提升进程的映射互相不可见——用 `runas /trustlevel:0x20000 "cmd /c net use"` 对比
   - 用户桌面能看到≠当前进程能看到（不同 logon session / 权限级别）
3. **UNC 直连**：`\\NAS_IP\share\...`，匿名通常被拒（错误 67 = 共享名不存在或凭据不足；1702 = 枚举失败）。共享有 valid users 白名单，**SMB 账户名 ≠ SSH 账户名**（绿联 NAS：SMB 用中文名/手机号，SSH 用系统账户）。
4. **SSH/SFTP 绕行（最可靠，有 SSH 凭据时优先）**：
   - 绿联 NAS SFTP 根 = `/`，共享目录映射为根下同名：`/volume1/HMSJ_B` → `/HMSJ_B`（与磁盘路径不同！）
   - **SFTP stat 可能报 "Operation unsupported"**，`sftp.get/put` 依赖 stat 会挂 → 用 `sftp.open(path, 'rb'/'wb')` 手动读写字节
   - paramiko 5.x：`pip install paramiko` 到独立 Python（Hermes venv 无 pip，用系统 Python）

## Eagle 导入（详见 eagle skill）
- **Python urllib 连 localhost:41595 必须绕过系统代理**：`urllib.request.build_opener(urllib.request.ProxyHandler({}))`，否则 ConnectionRefused
- **API 路径必须带 /api 前缀**（`/api/folder/list`、`/api/item/info`、`/api/item/addFromPaths`），漏掉返回 404
- 导入：`POST /api/item/addFromPaths` body `{"paths": [...], "folderId": "..."}`，中文用 `ensure_ascii=False`
- **导入后必须验证**：`/api/item/info?id=...` 查 name/ext/width/height/size 是否匹配

## 质量验收（交付前必做）
1. 参数验证：帧数、尺寸、时长、循环、体积（<目标）
2. **视觉验收**：原图 vs 压缩版拼对比图（首帧 + 中段帧各一行，附细节放大区），用 vision 检查：色彩是否偏灰偏冷（调色板 bug 特征）、色带/噪点、细节损失
3. 交付多档位让用户选（帧率/体积矩阵），确认后写回目标位置

## 陷阱清单
- PIL 调色板索引错位 → 颜色整体偏灰（见"核心坑"）
- `dither=None` 不生效，必须 `Image.Dither.NONE`
- gifsicle 无 `--fps`
- 降色对复杂内容收益小，别指望 128 色省一半
- 抽帧用均匀采样（首尾保留），不要简单切片
- optimize=True 不一定比 False 小（共享调色板下偶发反效果），两档都试
