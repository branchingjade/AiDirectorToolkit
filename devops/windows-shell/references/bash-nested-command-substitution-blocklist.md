# bash 内联嵌套命令替换触发 hardline blocklist（sed + $(grep)）

## 症状

```bash
cd ~/AppData/Local/hermes/hermes-agent/gateway && sed -n "$(grep -n 'def _refresh_fallback_model' run.py | cut -d: -f1),+40p" run.py
```

返回：

```
BLOCKED (hardline): command parser limit or malformed executable payload.
This command is on the unconditional blocklist and cannot be executed via the agent
— not even with --yolo, /yolo, approvals.mode=off, or cron approve mode.
RECOVERY: ... run: terminal(command="bash C:\...\blocked-<ts>.sh"). Do not retry inline.
```

命令被保存到 `~/AppData/Local/hermes/cache/blocked-scripts/blocked-*.sh` 供人工复核。

## 根因

`sed -n "$(grep ... | cut -d: -f1),+Np"` 这种**嵌套命令替换**（command substitution 内嵌另一个带引号/管道的命令）被 hardline 命令解析器的复杂度/不可解析性检测拦下。不是安全违规，是解析器限制。同一会话里反复出现（2026-08-07 实测两次）。

## 修法：拆成两步，绝不嵌套

```bash
# 1. 先单独拿行号
grep -n "def _refresh_fallback_model" run.py
# 2. 用字面行号单独跑 sed（上一步输出的实际行号）
sed -n '8415,8460p' run.py
```

或者一条命令但不用命令替换定位行号——用 `grep -A 40` 直接带上下文：

```bash
grep -n -A 40 "def _refresh_fallback_model" run.py
```

## 相关坑

- 同样会被拦的形态：`sed -n "$(grep ... | cut -d: -f1),+30p"`、`head -$(wc -l < f)` 等任何「命令替换结果作为另一个命令参数」的组合。
- search_files 工具对 Windows 反斜杠绝对路径会间歇报 IO error（rg 路径转换问题）——排查代码时终端 fallback 就靠上面的拆分式 grep/sed。
- 被拦命令本身没有执行、无副作用，只是浪费一轮；按 RECOVERY 提示跑 `bash blocked-*.sh` 是人工复核通道，agent 不需要走它，直接拆分重写即可。
