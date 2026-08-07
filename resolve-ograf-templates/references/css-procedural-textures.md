# CSS 纯代码质感纹理技术

> OGraf 环境不支持外部图片加载，所有纹理必须通过 CSS/SVG 内联生成。

## 核心原理

CSS 能达到的质感上限：
- **金属深度**：7-8 层 `text-shadow` 堆叠（环境光→背光→实体阴影→暗部龟裂→边缘高光→轮廓光→镜面反射）
- **木纹/噪点**：SVG `<feTurbulence>` 通过 data URI 嵌入 `background-image`
- **做旧边框**：`border-image` + 不规则透明度 `linear-gradient` 模拟磨损金漆
- **暗角**：4 级 `radial-gradient`（transparent→0.3→0.6→0.85）压缩视觉重心

## 木纹纹理（data URI SVG）

```css
background-image: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='200'><filter id='w'><feTurbulence type='fractalNoise' baseFrequency='0.015 0.1' numOctaves='4' seed='3'/><feColorMatrix type='matrix' values='0.12 0 0 0 0  0.06 0 0 0 0  0.03 0 0 0 0  0 0 0 0.35 0'/></filter><rect width='100%' height='100%' filter='url(#w)'/></svg>");
```

关键参数：
- `baseFrequency='0.015 0.1'`：X 方向低频（横向纹理），Y 方向高频（垂直压缩）→ 木纹条状
- `feColorMatrix`：RGB 通道映射棕色（0.12/0.06/0.03），A 通道控不透明度（0.35）
- 配合 `mix-blend-mode: overlay` 叠加到底色上

## 噪点颗粒（data URI SVG）

```css
background-image: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='200' height='200'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.6' numOctaves='3'/><feColorMatrix type='matrix' values='0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.07 0'/></filter><rect width='100%' height='100%' filter='url(#n)'/></svg>");
```

- `baseFrequency='0.6'`：高频 → 细小颗粒
- A 通道 0.07 → 极淡噪点
- 配合 `mix-blend-mode: screen` + `background-repeat: repeat`

## 8 层金属文字阴影

```css
text-shadow:
  0 0 25px rgba(200,160,100,0.45),   /* 环境辉光 */
  0 0 50px rgba(180,140,80,0.2),      /* 背光散射 */
  0 4px 8px rgba(0,0,0,0.85),         /* 实体投影 */
  4px 4px 0 rgba(60,25,10,0.65),      /* 暗部厚度 */
  5px 5px 0 rgba(0,0,0,0.5),          /* 最深阴影 */
  -1px -1px 1px rgba(240,200,140,0.35),/* 左上边缘光 */
  1px -2px 0 rgba(220,180,120,0.2),   /* 轮廓高光 */
  0 1px 0 rgba(255,220,160,0.1);      /* 顶部镜面反射 */
```

## 做旧金框（border-image）

```css
border-top: 3px solid;
border-image: linear-gradient(
  90deg,
  rgba(180,140,80,0) 0%,      /* 边缘消失 */
  rgba(180,140,80,0.75) 6%,   /* 突然出现（磨损断面） */
  rgba(200,160,100,0.35) 12%, /* 淡（剥落处） */
  rgba(180,140,80,0.85) 22%,  /* 浓（完整处） */
  rgba(140,100,50,0.2) 38%,   /* 几乎磨光 */
  rgba(200,160,100,0.6) 52%,  /* 半保留 */
  rgba(160,120,60,0.25) 68%,  /* 磨损 */
  rgba(200,160,100,0.7) 82%,  /* 最后一段完整 */
  rgba(180,140,80,0) 100%     /* 另一端消失 */
) 1;
```

- `1` 是 border-image-slice，对渐变 border 必须设为 1
- box-shadow `inset` 120px 暗边配合，增强匾额空间感

## 多重 CSS 模拟三层噪声

不用 SVG 的情况下：
```css
background:
  repeating-linear-gradient(1deg, transparent 0, transparent 2px, rgba(100,50,20,0.4) 2px, rgba(100,50,20,0.4) 3px),
  repeating-linear-gradient(89deg, transparent 0, transparent 5px, rgba(60,30,10,0.2) 5px, rgba(60,30,10,0.2) 6px),
  repeating-linear-gradient(179deg, transparent 0, transparent 8px, rgba(40,15,5,0.1) 8px, rgba(40,15,5,0.1) 9px);
```

三层交叉角度（1°/89°/179°）模拟木纹纤维交错。

## 质感上限判断

| 效果 | CSS 能达成 | 需要位图素材 |
|------|:--:|:--:|
| 木纹条理 | ✅ feTurbulence | |
| 噪点颗粒 | ✅ feTurbulence | |
| 金属深度 | ✅ 8层 shadow | |
| 做旧边框 | ✅ border-image | |
| 浮雕文字 | ⚠️ 近似 | ✅ 真实凹凸需要法线贴图 |
| 龟裂金箔 | ⚠️ 噪点模拟 | ✅ feTurbulence 可近似但不够 |
| 真实旧纸纤维 | ❌ | ✅ 需要扫描素材 |
| 锈蚀渗透 | ❌ | ✅ 需要素材 + blend 模式 |

## 关键陷阱：SVG 滤镜注入方式

**错误**：通过 innerHTML 注入 `<svg>` 元素，然后用 CSS `filter: url(#id)` 引用。
→ 滤镜 ID 不在 DOM 作用域内，CSS 无法引用。

**正确**：用 `encodeURIComponent` 生成 data URI，通过 CSS `background-image` 应用：
```javascript
var SVG = 'data:image/svg+xml,' + encodeURIComponent("<svg>...</svg>");
// 在 style 中: background-image: url(" + SVG + ")
```

**注意**：data URI 中的 SVG 必须用单引号包围属性值（因为外层是双引号的 JS 字符串），或者用 `encodeURIComponent` 完全编码。
