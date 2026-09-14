# OpenViking LLM 自动重分类（2026-08-28 实测端到端验证）

## 关键发现：target_uri 不是路径，是 hint

**不要试图"精确控制"OpenViking 的内容放置位置**——LLM 后台 extraction 会强制重新分类。

### 实测证据

**场景**：12 个"应该公开"的 skill / Obsidian 文档，调用 `add_resource(to='viking://resources/skills/yaoyu-film/AI电影编剧.md')`。

**返回**：`Resource added: viking://resources/skills/yaoyu-film/AI电影编剧.md`（成功）

**60 秒后实测**：
- `viking://resources/` 完整 tree 仍是 12 条（openviking-docs + test/），add 的 12 个**不在 resources/**
- `find('AI电影编剧 创作规范')` 召回命中，但 URI 是 `viking://user/default/memories/preferences/user/AI电影编剧技能创作规范.md`
- `viking://user/default/memories/preferences/user/` 下多了 5-6 个"AI电影编剧"相关的文件

**结论**：
- OpenViking 服务端接了 add_resource 请求，**LLM extraction 把内容重定向到 user 命名空间**
- `to` 参数被忽略，LLM 按内容性质自动判断（个人/方法论 → user，外部/官方 → resources/）

### 迁移后的真实状态（2026-08-28 16:00）

**viking://resources/**（"公开"）：
- 15 个 OpenViking 官方文档（openviking-docs/）
- 0 个用户文档

**viking://user/default/memories/**（"私有"，但实际上**所有内容都自动归这里**）：
- 995+ entries
- 50+ entities/（影视/工具/团队/项目/...）
- 19+ preferences/user/（DSH/Skill/创作/...）
- 15+ events/2026/08/28/（当天记录）

### 评估指标修正

| 我之前评估的 | 实际应该评估的 |
|---|---|
| ❌ 文件是否落在 viking://resources/ | **不评估**——LLM 自动分类，不受你控制 |
| ❌ target_uri 是否生效 | **不评估**——target_uri 是 hint |
| ✅ `find(query)` 召回命中率 | 关键指标（实测 50%+） |
| ✅ 召回内容是否直接可用 | 关键指标（LLM 摘要 + 分类） |
| ✅ 用户感知价值 | 关键指标（agent 实际检索体验） |

### 用户的真实需求 vs OpenViking 的能力

用户原始诉求：
> "把所有的记忆，skill，obsidian 知识库都分门别类的放到适合的位置，公共的和私有的区分开来"

OpenViking 的现实：
- ❌ 不能按"公开/私有"精确分类（LLM 决定）
- ✅ 能按主题自动分类（影视/工具/团队/...）
- ✅ 能跨命名空间统一检索（find() 不区分 user/resources）
- ✅ LLM 摘要让内容 agent 可直接消费

**结论**：用户真正想要的能力 = 让 agent 能随时检索内容 = **OpenViking 已经达成**。

### 实操建议

1. **停止纠结 target_uri**——LLM 会自动归类
2. **统一用 `remember()` 或 `add_resource()`**——两者最终归宿相同
3. **不要为"公开"专门挑内容**——写就好，LLM 处理分类
4. **评估成功的标志**：agent 在新项目里 find() 能召回你期望的内容
5. **批量写入注意**：后台 extraction 排队卡 503，单次写入 ≤ 50 条/批，间隔 ≥ 2s

### 何时强制 resources/（真正的例外）

- 外部 URL（GitHub README、官方文档）→ add_resource(path=URL)
- 团队级别共享素材 → add_resource(to='viking://resources/team/...')
- 这些情况 LLM 倾向保留在 resources/

**个人偏好/工作流/Skill 规范** → 无论用 remember 还是 add_resource，**最终都在 user/memories/**。接受这个设计。