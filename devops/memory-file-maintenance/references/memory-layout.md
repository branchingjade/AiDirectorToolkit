# MEMORY.md 文件结构

## 文件位置

- 默认：`~/AppData/Local/hermes/memories/MEMORY.md`（Windows: `C:\Users\HMSJ\AppData\Local\hermes\memories\MEMORY.md`）
- 备份命名：`MEMORY.md.bak-YYYYMMDD-pre-<目的>`（如 `pre-optimize` / `pre-slim` / `pre-cleanup`）
- 历史备份残留：旧 .bak.<unix_timestamp> 格式（自动生成），可清理

## 结构

- **开头**：`安全红线...` 单行（非段）
- **段分隔符**：单独一行 `§`（空行包围）
- **段格式**：段首文本 + `\n\n` + 段内容 + `\n\n§\n\n` + 下一段首文本
- **段内容**：1 行到多行，长度不限

## parts 索引映射（Python re.split）

```python
import re
text = open("MEMORY.md", encoding="utf-8").read()
parts = re.split(r"(?m)^§$", text)
# parts[0] = "安全红线..." 开头（非段）
# parts[1] = 段 1 的内容
# parts[N] = 段 N 的内容（段号 N 对应 parts[N]）
# parts[0] 是开头，不是段 0
```

**段号 N 对应 parts[N]**，不是 parts[N-1]。这是 2026-08-26 实测踩坑——很多代码错误地写 `parts[N-1]` 导致 anchor 错位。

## 容量规则

- 工具上限：16000 字符
- 警告阈值：~66% 占用（~10560 字）
- 拒写阈值：>16000 字符（工具直接报错）
- 段数限制：无硬上限（实测 ≤40 段为佳）

## § 出现次数 vs 段数

- N 段 → § 出现 N+1 次（段间 N-1 个 + 文件首尾可能各 1 个）
- 自检脚本里 § 数量 == 段数 + 1 ≈ 验证段分隔符齐全

## 段间分隔的精确格式

```
[段 N 内容，可能多行]

§
[段 N+1 内容]
```

注意：`§` 是单独一行，前后都有空行。Python `re.split(r"(?m)^§$", text)` 只切 `§` 那行本身，前后空行**不会**切走，所以切完后相邻段之间还有 `\n\n`。