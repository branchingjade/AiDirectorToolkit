# CSS 材质模拟技术 & 限制

> 金漆匾额模板打磨过程中积累的 CSS 材质模拟手段和硬上限。

## 可达到的（CSS 极限 ~60-70% 真实感）

### 多层 text-shadow 模拟金属深度
```
text-shadow:
  0 0 25px rgba(200,160,100,0.4),    ← 外层辉光
  0 4px 8px rgba(0,0,0,0.8),         ← 底层暗影（模拟凹陷）
  4px 4px 0 rgba(80,40,20,0.55),     ← 右下投影（模拟雕刻厚度）
  0 0 3px rgba(220,180,120,0.4),     ← 中心高光
  -1px -1px 0 rgba(0,0,0,0.4)        ← 左上暗边（模拟笔画边缘）
```

### 木纹纹理（双层线性渐变交错）
```css
background:
  repeating-linear-gradient(2deg, transparent, transparent 3px, rgba(80,40,15,0.3) 3px, rgba(80,40,15,0.3) 4px),
  repeating-linear-gradient(88deg, transparent, transparent 7px, rgba(60,30,10,0.15) 7px, rgba(60,30,10,0.15) 8px)
```

### 金框斑驳（border-image 渐变，不规则 alpha）
```css
border-image: linear-gradient(90deg,
  rgba(180,140,80,0) 0%,
  rgba(180,140,80,0.7) 6%,
  rgba(180,140,80,0.3) 12%,
  rgba(180,140,80,0.8) 22%,
  rgba(140,100,50,0.15) 38%,
  rgba(200,160,100,0.55) 52%,
  rgba(200,160,100,0.65) 82%,
  rgba(180,140,80,0) 100%
) 1
```

### 暗角压暗
```css
background: radial-gradient(ellipse at 45% 45%, transparent 30%, rgba(0,0,0,0.55) 80%, rgba(0,0,0,0.8) 100%)
```

## CSS 做不到的（需要 SVG / 位图素材）

| 效果 | CSS 能模拟？ | 替代方案 |
|------|:---:|------|
| 金箔龟裂纹理 | 否 | SVG feTurbulence + feDisplacementMap |
| 真实木纹（年轮/结疤） | 否 | 位图素材叠加 |
| 金属光泽（多角度反光） | 否 | linear-gradient 可做单向高光，做不到真实反射 |
| 印泥晕染边缘 | 否 | SVG feGaussianBlur + feTurbulence |
| 漆面磨损划痕 | 否 | 多层位图 + mix-blend-mode |
| 3D 立体雕刻深度 | 否 | CSS 只能模拟 ~2px 视觉深度 |

## SVG feTurbulence 噪点

```html
<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%">
  <filter id="noise">
    <feTurbulence type="fractalNoise" baseFrequency="0.65" numOctaves="3"/>
    <feColorMatrix type="saturate" values="0"/>
  </filter>
  <rect width="100%" height="100%" filter="url(#noise)" opacity="0.12"/>
</svg>
```

注意：feTurbulence 在 CEF 中性能差。OGraf 逐帧渲染时不要每帧重新生成。

## 决策树

```
需要材质效果？
├─ 金属/立体 → CSS text-shadow ≥5层 （60%真实度）
├─ 木纹/织物 → CSS repeating-linear-gradient 双层交错（50%）
├─ 龟裂/磨损 → SVG feTurbulence（70%，CEF注意性能）
├─ 照片级纹理 → 位图素材叠加（100%，需外部素材）
└─ 3D雕刻/浮雕 → 位图素材（CSS做不到）
```
