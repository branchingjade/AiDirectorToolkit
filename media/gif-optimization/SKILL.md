---
name: gif-optimization
description: 压缩GIF动图到指定体积/分辨率，保持动画。触发词：GIF压缩、动图压缩、压到5MB内、动态封面。
---

# GIF 动图压缩优化

## 触发条件
用户要求把 GIF 动图压缩到指定体积内（如"5MB内"）或指定分辨率（如 353×496）。GIF 是**动图**——必须逐帧处理，禁止当静态图只处理第一帧（会丢动画）。影视用户高频场景：Eagle 动态封面 gif 超限需压缩。

## 铁律（实测踩坑）

1. **共享调色板禁止 `convert('P')` + `putpalette()` 组合**——每帧先自适应量化再强行换共享调色板，索引错位导致整体偏灰偏冷、颜色全乱。**必须用 `fr.quantize(palette=共享P帧, dither=...)`** 逐帧映射到共享调色板，颜色才正确。
2. **dither 参数必须是 `Image.Dither.NONE` / `Image.Dither.FLOYDSTEINBERG` 枚举**——传 `dither=None` 无效（静默 fallback 到默认抖动），体积数字完全不变，容易误判"抖动没影响"。
3. **抖动与体积的权衡**：FLOYDSTEINBERG 抖动模拟渐变、色彩自然，但噪点破坏 LZW 压缩，体积显著增大；NONE 体积小但渐变区出现色带。照片级真人 GIF：74帧 256色 抖动 5.79MB vs 无抖 2.65MB——差一倍。
4. **照片级真人 GIF 体积规律**：110帧/706×992/17.4MB 的源，缩到 353×496 后仍超 5MB——**全帧（25fps）压不进，必须抽帧**。实测：74帧(16.7fps) 256色 ≈5.7-5.8MB 超限；55帧(12.5fps) 256色 4.29MB 达标。约束内先保色彩数（256）再降帧率。
5. **抽帧后帧时长要翻倍保持总时长**（110帧×40ms → 55帧×80ms ≈ 4.4s 不变），`loop=0` 保持无限循环。

## 标准流程

### 1. 分析源
```python
from PIL import Image
im = Image.open(src)
n = im.n_frames          # 帧数
for i in range(n):
    im.seek(i)
    durations.append(im.info.get('duration', 40))  # 每帧时长
# 记录: 帧数/尺寸/总时长/duration 列表
```

### 2. 逐帧缩放 + 共享调色板（正确写法）
```python
TARGET = (353, 496)
rgb_frames = []
for i in range(n):
    im.seek(i)
    rgb_frames.append(im.convert('RGB').resize(TARGET, Image.LANCZOS))

# 共享调色板基于首帧生成
pal = rgb_frames[0].quantize(colors=256, method=Image.Quantize.MEDIANCUT,
                             dither=Image.Dither.NONE)
# 每帧正确映射到共享调色板（关键！）
p_frames = [fr.quantize(palette=pal, dither=Image.Dither.FLOYDSTEINBERG) for fr in rgb_frames]
p_frames[0].save(out, save_all=True, append_images=p_frames[1:],
                 duration=durations, loop=0, optimize=True)
```

### 3. 候选档位矩阵（一次跑完选最优）
- 全帧 / 抽帧（`[::2]`→55帧、`[i for i in range(n) if i%3!=2]`→74帧）× 颜色(256/192/128) × 抖动(on/off)
- 每个档位输出独立文件并打印 MB，挑 **达标且质量最高**（颜色优先，其次帧率）

### 4. 视觉验证（必须做，体积达标≠质量达标）
生成并排对比图：原图首帧（缩放）| 压缩首帧 | 各自细节放大区（NEAREST 放大），用 vision_analyze 评估色彩偏差/色带/细节损失。128 色调色板对照片级画面**不可接受**（色块+色彩失真），256 色+抖动才接近原图。

## 备选：gifsicle（黄金标准工具）

Windows 二进制下载：`https://eternallybored.org/misc/gifsicle/releases/gifsicle-1.95-win64.zip`（内附 gifdiff.exe）。

```bash
gifsicle --resize 353x496 --optimize=3 --colors 256 -o out.gif in.gif
```

- `--optimize=3` 最强压缩；局部调色板优化，同样帧数/色数下比 PIL 体积小
- **注意：1.95 版没有 `--fps` 选项**（会报 unrecognized option）——抽帧用 PIL 先做，或接受 gifsicle 的全帧输出
- 实测：110帧 256色 optimize=3 = 7.86MB，同样超 5MB 约束，仍需先抽帧

## 处理 Eagle 库中的 GIF（影视用户高频场景）

Eagle 素材（"动态封面"类 gif）处理链路：
1. `/api/item/info?id=<ID>` 拿元数据（ext/size/width/height）——确认是 gif 动图
2. 库盘不可达（Y: 未挂载）时走 NAS SSH/SFTP 兜底，见 `eagle` skill 第 12 节 + `ugreen-nas-deploy` skill
3. 处理完 SFTP 覆盖回库文件，`metadata.json` 不动，Eagle 自动重新索引

## 输出规范
- 输出文件命名带参数：`压缩_动态封面_74f_c256.gif`（帧数+色数），便于多档对比
- 交付前报告：最终体积、帧率（fps）、总时长、与源对比的取舍（降帧 or 降色）
- 用户目标通常是"5MB内"上限——达标后若有余量，说明更高帧率/色数的替代档位，让用户选
