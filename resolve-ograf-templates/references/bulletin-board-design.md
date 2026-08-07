---
title: 公告栏风格人名条设计模式
type: 设计参考
created: 2026-07-16
tags:
  - 人名条
  - 设计模式
  - 公告栏
---

# 公告栏风格人名条设计模式

## 概念

模仿 1990 年代工厂/单位公告栏的视觉语言——旧纸张、铅印宋体、红印章、手写通知的质感。

## 核心元素

| 元素 | 实现 | 配色 |
|------|------|------|
| 旧纸底 | SVG feTurbulence data URI 噪波 | #e8dcc8（米黄） |
| 铅印文字 | 宋体 SimSun + text-shadow | #2a1f14（深褐墨） |
| 分隔线 | linear-gradient 透明渐变 | 同文字色 |
| 红印章 | CSS border + 内嵌文字 | #8b3a2a（铁锈红） |
| 角落墨迹 | CSS radial-gradient 圆点 | rgba(42,31,20,0.08) |

## SVG 噪波纹理

```javascript
var PAPER_SVG = 'data:image/svg+xml,' + encodeURIComponent(
  "<svg xmlns='http://www.w3.org/2000/svg' width='300' height='200'>" +
  "<filter id='paper'>" +
  "<feTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='4' seed='2' result='noise'/>" +
  "<feColorMatrix type='matrix' in='noise' values='" +
  "0 0 0 0 0.91  0 0 0 0 0.86  0 0 0 0 0.78  0 0 0 0.12 0'/>" +
  "</filter>" +
  "<rect width='100%' height='100%' filter='url(#paper)' fill='#e8dcc8'/>" +
  "</svg>"
);
```

## HTML 结构

```html
<!-- 底部30%人名条容器 -->
<div style="position:absolute;top:70%;left:0;right:0;height:30%;overflow:hidden">
  <!-- 纸张底色 -->
  <div style="position:absolute;inset:0;background:#e8dcc8"></div>
  <!-- SVG噪波纹理叠加 -->
  <div style="position:absolute;inset:0;opacity:0.8;
    background-image:url(PAPER_SVG);background-repeat:repeat;background-size:300px 200px">
  </div>
  <!-- 暗角压暗 -->
  <div style="position:absolute;inset:0;
    background:radial-gradient(ellipse at 50% 50%,transparent 40%,rgba(0,0,0,0.1) 100%)">
  </div>
  <!-- 内容区 -->
  <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center">
    <!-- 人名 -->
    <div style="font-size:48px;font-weight:bold;color:#2a1f14;
      font-family:SimSun,serif;
      text-shadow:0 1px 0 rgba(0,0,0,0.3),0 0 1px rgba(42,31,20,0.2)">
      陈 强
    </div>
    <!-- 分隔线 -->
    <div style="width:60px;height:1.5px;
      background:linear-gradient(90deg,transparent,#4a3a2a,transparent);
      margin:8px auto;opacity:0.4"></div>
    <!-- 角色 -->
    <div style="font-size:20px;color:#4a3a2a;opacity:0.55;
      font-family:SimSun,serif">
      强盛安保 总经理
    </div>
  </div>
  <!-- 红印章 -->
  <div style="position:absolute;right:8%;bottom:20%;
    width:32px;height:32px;border:2px solid #8b3a2a;
    display:flex;align-items:center;justify-content:center;opacity:0.65">
    <span style="font-size:14px;color:#8b3a2a;font-weight:bold;font-family:SimSun,serif">印</span>
  </div>
</div>
```

## 可调参数

| 参数 | 默认值 | 范围 | 说明 |
|------|--------|------|------|
| nameSize | 48 | 28-72 | 人名字号 |
| nameSp | 6 | 0-16 | 人名字距 |
| subSize | 20 | 14-30 | 角色字号 |
| subSp | 4 | 0-12 | 角色字距 |
| subOp | 0.55 | 0.2-0.9 | 角色透明度 |
| c1 | #2a1f14 | - | 人名墨色 |
| c2 | #4a3a2a | - | 角色字色 |
| c3 | #4a3a2a | - | 分隔线色 |
| c4 | #8b3a2a | - | 印章色 |

## 注意事项

- **OGraf 坐标系**：`bottom:0` 渲染在上半部分，用 `top:70%` 替代
- **SVG 必须用 data URI**：innerHTML 注入的 SVG filter 不生效
- **animTime 初始值**：设为 animDur 确保预览可见完整设计
- **text-shadow 用 rgba**：hex 带 alpha 在部分浏览器不支持
