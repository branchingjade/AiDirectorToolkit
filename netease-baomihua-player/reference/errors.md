# 错误处理指南

本文档描述 `bmh-cli.exe` 可能返回的所有错误码及处理方式。

---

## 错误响应格式

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error description"
  }
}
```

---

## 错误码详解

### APP_NOT_INSTALLED
- **含义**：爆米花客户端未安装
- **触发命令**：`start`, `search`, `play`
- **处理方式**：提示用户从 https://baomihua.163.com 下载安装
- **示例回复**："爆米花尚未安装，请先前往 https://baomihua.163.com 下载安装。"

### APP_OFFLINE
- **含义**：客户端未运行且无法连接服务
- **触发命令**：`search`, `play`（自动启动失败时）
- **处理方式**：执行 `start` 命令尝试启动
- **示例回复**："爆米花未在运行，正在尝试启动..."

### SERVICE_UNAVAILABLE
- **含义**：客户端进程存在但 HTTP 服务不可用
- **触发命令**：所有需要服务的命令
- **处理方式**：等待 3-5 秒后重试，或提示用户重启爆米花
- **示例回复**："爆米花服务暂时不可用，请稍等片刻或重启爆米花。"

### START_TIMEOUT
- **含义**：启动爆米花后 15 秒内服务未就绪
- **触发命令**：`start`
- **处理方式**：提示用户手动启动爆米花
- **示例回复**："爆米花启动超时，请尝试手动启动。"

### LAUNCH_FAILED
- **含义**：CreateProcess 调用失败，无法启动爆米花进程
- **触发命令**：`start`
- **处理方式**：检查安装路径是否正确，或提示用户重新安装
- **示例回复**："启动爆米花失败，请检查是否安装正确。"

### INVALID_PARAMS
- **含义**：命令参数不完整或格式错误
- **触发命令**：所有命令
- **处理方式**：检查参数是否正确
- **常见原因**：
  - search 缺少 `--keyword`
  - play 缺少 `--media-type` 或 `--tmdb-id`
  - 电视剧缺少 `--season` 或 `--episode`
  - `--media-type` 传了非 2/3 的值

### MEDIA_NOT_FOUND
- **含义**：请求播放的媒体在爆米花媒体库中未找到
- **触发命令**：`play`
- **处理方式**：确认 TMDB ID 是否正确，或先执行 search 确认媒体库中有该内容
- **示例回复**："未找到该影片，可能媒体库中没有此内容。"

### UNAUTHORIZED
- **含义**：Auth-Code 认证失败
- **触发命令**：`search`, `play`
- **处理方式**：CLI 工具版本与客户端版本不匹配，需更新 skill 包
- **示例回复**："认证失败，请检查 CLI 工具是否为最新版本。"

### TIMEOUT
- **含义**：HTTP 请求超时
- **触发命令**：所有需要服务的命令
- **处理方式**：重试请求
- **示例回复**："请求超时，正在重试..."

### BACKEND_ERROR
- **含义**：爆米花服务端内部错误
- **触发命令**：`search`, `play`
- **处理方式**：重试，或提示用户重启爆米花
- **示例回复**："服务出现异常，请稍后重试或重启爆米花。"

---

## 错误处理最佳实践

1. **先 doctor 后操作**：执行 search/play 前先 doctor 确认状态
2. **自动重试**：TIMEOUT 和 BACKEND_ERROR 可自动重试一次
3. **自动启动**：search 和 play 内置自动启动，多数情况无需手动处理 APP_OFFLINE
4. **用户友好**：将错误码转化为自然语言，不要直接暴露 error code 给用户

---

## 错误码速查表

| 错误码 | 含义 | 处理方式 |
|--------|------|---------|
| `APP_NOT_INSTALLED` | 爆米花未安装 | 提示用户安装 |
| `APP_OFFLINE` | 客户端未运行 | 执行 `start` 命令 |
| `SERVICE_UNAVAILABLE` | 服务不可用 | 等待或重启爆米花 |
| `START_TIMEOUT` | 启动超时 | 提示用户手动启动 |
| `LAUNCH_FAILED` | 启动进程失败 | 检查安装路径 |
| `INVALID_PARAMS` | 参数错误 | 检查命令参数 |
| `MEDIA_NOT_FOUND` | 媒体未找到 | 确认 ID 是否正确 |
| `UNAUTHORIZED` | 认证失败 | 更新 CLI 工具 |
| `SERVICE_DISABLED` | AI 扩展功能被服务端禁用 | 联系管理员或等待恢复 |
| `TIMEOUT` | 请求超时 | 重试请求 |
| `BACKEND_ERROR` | 后端错误 | 重试或重启爆米花 |
