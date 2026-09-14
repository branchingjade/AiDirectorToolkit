# TencentDB Agent Memory: 环境变量 + Skill 数据 + Feishu(2026-08-26 补充)

## 环境变量传递陷阱

`setx` 只改注册表供新进程,不传给已运行 gateway。`hermes gateway start` 直接 spawn,绕过计划任务。

验证: `psutil.Process(<pid>).environ().get('MEMORY_TENCENTDB_GATEWAY_HOST')`

Plugin `is_available()` 返回 True 但 NAS 端无请求→检查 gateway-stdio.log 有无 memory-tencentdb 日志。Plugin hooks 需实际对话写入记忆才触发。

## Skill 数据存储

Skill 走 L0(conversations)层,不走 L1(memories)层:
- `/search/conversations` 可搜(score 0.797) ✓
- `/search/memories` 搜不到(L1 LLM 提取 0 条) ✗

skill/文档类数据用 `/search/conversations` 搜索。

## Feishu adapter 失败

Gateway 启动报 "Platform 'Feishu / Lark' config validation failed"。需检查飞书依赖或 config。memory_tencentdb 插件本身 active,但飞书平台适配器不可用。

## 多模态缺口

`/capture` 只收 string,无 image/file/base64。bot 想记住图须 OCR→文字→capture。PDF 不进 hub。
