# 按任务类别聚类 token 消耗

回答「哪类任务消耗 token 最多」的标准脚本。按会话标题正则归类，统计 tokens / 费用 / 推理 / 工具调用。实测于 2026-08-08（910 会话，84M tokens）。

## 完整脚本

```python
import sqlite3, re, collections
# WAL 模式下不能 cp 副本（会是空库），只读直连原文件
db = sqlite3.connect('file:C:/Users/<user>/AppData/Local/hermes/state.db?mode=ro', uri=True)
cur = db.cursor()
rows = cur.execute('''SELECT title, source, input_tokens, output_tokens, reasoning_tokens,
                             estimated_cost_usd, message_count, tool_call_count
                      FROM sessions WHERE title IS NOT NULL AND title != '' ''').fetchall()
# 类别顺序重要：先匹配最具体的；正则里不要写 \( 转义（会匹配字面括号导致全部落空）
cats = [
    (r'(伏妖记|犬子无双|导演|编剧|分镜|剧本|短剧|电影|分场|台本|达芬奇|人名条|提示词|Seedance|生图|Blender|品鉴)', '影视创作/提示词'),
    (r'(TTS|语音|朗读|豆包|音频|配乐|音乐|音色|配音|歌词|音分)', '语音音频'),
    (r'(文档|API|MDN|总结|分类|统计|整理)', '文档整理'),
    (r'(排查|修复|Hermes|gateway|配置|升级|补丁|监控|cron|看板|故障|兜底|部署|MCP|Clash|alist|NAS|Eagle|token 检查|网关|WebBridge|浏览器|扩展|git push)', '运维排查'),
    (r'(技能|skill|知识库|研习|大师|题材|导演美学)', '知识库研习'),
    (r'(飞书|评论|会话|成员|画像|协作|记忆|Obsidian|测试|确认|问候|greeting)', '飞书协作/测试'),
]
agg = collections.defaultdict(lambda: [0,0,0,0.0,0,0])  # 会话数, in+out, 推理, 费用, 消息, 工具调用
unmatched = collections.Counter()
for title, src, it, ot, rt, cost, mc, tc in rows:
    t = title or ''
    hit = False
    for pat, name in cats:
        if re.search(pat, t, re.I):
            a = agg[name]
            a[0]+=1; a[1]+=(it or 0)+(ot or 0); a[2]+=(rt or 0); a[3]+=(cost or 0); a[4]+=(mc or 0); a[5]+=(tc or 0)
            hit = True; break
    if not hit:
        unmatched[t] += 1
        a = agg['其他']
        a[0]+=1; a[1]+=(it or 0)+(ot or 0); a[2]+=(rt or 0); a[3]+=(cost or 0); a[4]+=(mc or 0); a[5]+=(tc or 0)
total_tok = sum(a[1] for a in agg.values())
for name, (c, tok, rt, cost, mc, tc) in sorted(agg.items(), key=lambda x: -x[1][1]):
    print(f'{name:<16}{c:>5}{(tok/1e6):>9.1f}M {tok/total_tok*100:>6.1f}% ${cost:>7.2f} tools{tc:>6}')
# 未分类的大头会话单独看，避免结论失真：
# for t, c in unmatched.most_common(20): print(t, c)
```

## 坑（都实测踩过）

1. **`cp` 副本是空库**——WAL 模式只复制主文件，`sqlite_master` 返回空表。必须 `mode=ro` URI 直连原文件。
2. **正则 `\\(` 转义陷阱**——类别正则里写成 `\\(伏妖记|...)` 会匹配字面括号，`re.search` 永不命中，所有会话落「其他」。用不转义的 `(`。
3. **SELECT 列数与解包数不匹配**——8 列查出来 for 循环解 9 个变量会 ValueError。数清列。
4. **「其他」类通常占比不小**（实测 15%）——里面常混着大量本可归类的创作碎片会话（提示词优化/达芬奇/场景名等），结论前先看未分类 top 列表，必要时扩正则。
5. **模型维度比任务维度更能说明费用**——flash vs pro 可能 token 量相近但费用差 3-5 倍；按模型分组看费用（`GROUP BY model`）是省钱分析的起点。
6. **⚠️ 无标题会话是最大遗漏源**（2026-08-08 实测）：子代理/delegate_task 会话约 60% 无标题（8 月 423 会话中 250 个无标题、占 44M tokens 超总量一半）——只按 `title IS NOT NULL` 过滤会漏掉大头，结论严重失真。必须 join `messages` 表取每个会话第一条 `role='user'` 消息做归类（首条消息=任务意图，如「研究黑泽明…产出研习报告」「写《X密码.md》」），再正则匹配。完整实现见 `scripts/task-cost-classify.py`；1.5GB 库全表扫 messages 首条消息约数秒~十几秒，可接受但别反复跑。
7. **费用口径：DeepSeek 按人民币计费**（用户明确要求）——不要报美元估算，按官方人民币价重算（flash 命中 0.02/未命中 1/输出 2 元每百万；pro 0.025/3/6）。定价表与计算函数见 `references/deepseek-cny-pricing.md`。缓存命中占输入量 95%+（长会话反复读同一上下文），命中价 1/50 是成本主降点。
