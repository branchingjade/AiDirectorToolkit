# OGraf 人名条定位技术

> 在 OGraf 预览区中定位人名条的正确方式

## 问题

OGraf 预览区的坐标系与标准 CSS 不同。使用 `bottom:0;height:35%` 时，人名条可能渲染在上半部分而非底部。

## 解决方案

使用 `top:70%;height:30%` 替代 `bottom:0;height:35%`：

```css
/* 错误 - 可能渲染在上半部分 */
position: absolute;
bottom: 0;
height: 35%;

/* 正确 - 底部 1/3 */
position: absolute;
top: 70%;
height: 30%;
```

## 验证方法

1. 注入模板后用 `vision_analyze` 截图检查实际位置
2. 如果位置不对，调整 `top` 值（70% = 底部 30%）
3. 高度建议 30-35%，符合人名条标准比例

## 完整定位示例

```javascript
// 人名条容器
'<div style="position:absolute;top:70%;left:0;right:0;height:30%;overflow:hidden">'
  // 背景层
  + '<div style="position:absolute;inset:0;background:#e8dcc8"></div>'
  // 内容居中
  + '<div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center">'
    + '<div style="font-size:48px;font-weight:bold;color:#2a1f14">陈 强</div>'
    + '<div style="font-size:20px;color:#4a3a2a">强盛安保 总经理</div>'
  + '</div>'
+ '</div>'
```

## 注意事项

- 每次修改后必须用 `vision_analyze` 验证实际渲染位置
- 不要假设 CSS 行为与标准浏览器一致
- OGraf 使用 CEF 渲染，但坐标系可能有特殊处理
