# ByteDance 视频超分/增强产品入口（2026-06 验证）

## 已确认的入口

| 页面 | URL | 状态 | 说明 |
|---|---|---|---|
| ModelArk 模型平台 | `https://www.byteplus.com/en/product/modelark` | ✅ 可访问 | 托管 Seedance 2.0（视频生成 4K）、Seedream 5.0 等 |
| Seedance 2.0 产品 | `https://www.byteplus.com/en/product/seedance` | ✅ 首页有入口 | 视频生成模型，支持 4K、视频编辑扩展 |
| BytePlus 首页 | `https://www.byteplus.com/en` | ✅ | 导航有 Products / Docs |
| Docs 首页 | `https://docs.byteplus.com/en/docs` | ✅ | 产品目录页（非具体文档） |

## 404 的页面

| URL | 结果 |
|---|---|
| `/en/product/video-enhancer` | SPA 壳加载但路由 404 |
| `/en/product/vision-ai` | 同上 |
| `/en/docs/byteplus-video-enhance` | 重定向到 `/en/docs` |
| `/en/docs/byteplus-video-editor` | 重定向到 `/en/docs` |
| `volcengine.com/product` | 404 "页面无法访问" |

## 关键结论

ByteDance 没有一个独立的 "Video Enhancer" / "Video Upscale" 产品页。
视频增强能力分散在：
- **Seedance 2.0**（通过 ModelArk API，生成时支持 4K、视频编辑扩展）
- **剪映/CapCut 桌面版**（消费者端 "智能超清" 功能，无独立产品页）
- **火山引擎视频智能**（国内版，具体产品页 URL 未能从 SPA 提取）

## 搜索技巧

- Bing 搜 "火山引擎 视频超分辨率" 会被拆成 "火山+引擎+视频+超分辨率"，返回火山百科
- BytePlus 站内搜索 "video enhancer" 返回的是文档条目，不返回产品页
- BytePlus 和 Volcengine 都是 React SPA，curl/无头浏览器难以提取内容
- 用 Kimi WebBridge 的 `evaluate + innerText` 可以提取 SPA 渲染后的文本
