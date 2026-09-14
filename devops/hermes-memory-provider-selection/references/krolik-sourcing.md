# MemOS Krolik 溯源与已知坑(2026-08-26 端到端实证)

> 这份是 SKILL.md 主体的"放大版参考资料"——只在评估 NAS MemOS 实例、查 Krolik 行为来源、写新坑兜底时翻。
> 主 SKILL.md 只留原则和命令,细节都在这里。

## 一、Krolik 是什么(确证结论,2026-08-26)

| 维度 | 事实 | 证据 |
| --- | --- | --- |
| Krolik 是 fork 吗 | ❌ 不是 | 全部代码在 `MemTensor/MemOS` 公开仓 `src/memos/api/` 下;`overlays/krolik/` 是空目录 |
| 是谁写的 | GitHub 用户 `Hustzdy` (`67457465+wustzdy@users.noreply.github.com`) | 首次合入 commit `c2bc36b15f`, 2026-02-06, PR #1040 |
| 合入时官方态度 | "某位开发者扩展后的 API 及部署配置,**仅供参考**。这些内容**尚未与云服务集成**,**仍处于测试阶段**" | `docs/cn/open_source/modules/api_deployment.md` L11(原话) |
| Krolik 加了什么 | 4 件事:**API Key 鉴权 / Redis 限流 / Admin 路由 / 安全响应头** | `src/memos/api/server_api_ext.py` L1-8 docstring 自己写的 |
| 关联域名 | `krolik.hully.one` / `memos.hully.one` | `server_api_ext.py` L84-86 CORS_ORIGINS |
| 作者邮箱 | `syzsunshine219@gmail.com` | commit `8553242` author metadata |

## 二、4 个"坑"的真实溯源

之前误归到 Krolik overlay,实际全部源自 MemTensor 上游 main:

| 坑 | 真实出处 | 你 NAS 镜像为什么有 |
| --- | --- | --- |
| `custom_tags` 字段被接受 + 覆写为 `["mode:fast"]` | MemTensor 上游 `add_handler.py` 抽取逻辑 | 主仓行为,NAS 镜像继承 |
| `info` 散到 metadata 顶层 | MemTensor 上游 | 2026-02-06 之后 `c2bc36b15f` 提交加 `exclude_fields` 过滤;你 NAS 镜像 build 时 base 比这更早,导致冲突未过滤 |
| `feedback` 必填 `history` | MemTensor 上游 schema | OpenAPI 文档漏标必填 |
| `delete_memory` 互斥但 silent failure | MemTensor 上游 | 上游代码本身这么实现 |

**确证 base commit 多老的命令**:

```bash
# 1. Krolik 首次合入 = 2026-02-06,commit c2bc36b15f
curl -s https://api.github.com/repos/MemTensor/MemOS/commits?path=src/memos/api/server_api_ext.py

# 2. c2bc36b15f 时 add_handler.py 已经有 exclude_fields
curl -s https://raw.githubusercontent.com/MemTensor/MemOS/c2bc36b15f/src/memos/api/handlers/add_handler.py | grep -c exclude_fields
# 输出: > 0

# 3. 你 NAS 实际 base commit
ssh HMSJ@192.168.1.2 "docker exec memos-server git -C /app log --oneline -1 2>/dev/null"
# 输出应该比 c2bc36b15f 早 → 这就是 info 散顶层的根因
```

## 三、客户端兜底位置

`scripts/memos_client.py`(标准库 only,265 行)已经按"已观察行为"做了兜底:

| 坑 | 兜底位置 |
| --- | --- |
| `id` 字段不是 `memory_id` | `search_print()` 用 `m.get("id")` 兼容 |
| `custom_tags` 被覆写 | docstring 标明"分类用 messages 文本带 tag" |
| `info` 散到顶层 | docstring 标明"用 topic/agent/proj/ts,别用 source/info/tags" |
| `feedback` 必填 history | `feedback()` 默认带 `history=[]` |
| `feedback` sync 慢 | `sync=False` 默认 |
| `delete` 互斥静默 | `delete()` 用参数互斥 + `data.status=="success"` 校验 |
| sync add 卡 30+s | `add(sync=True)` 加 `sync_timeout=45` |

新坑出现时按相同模式:在 `memos_client.py` docstring 标注观察现象 + 加参数默认值,SKILL.md 留一行短描述。

## 四、跟其他实例的行为偏差(迁移注意)

| 实例 | base commit | 行为是否跟 Krolik 一致 |
| --- | --- | --- |
| memos.cloud | MemTensor 当前 main(滚动更新) | 不一致——main 在演进,4 个坑可能已修 |
| memos-local-plugin 2.0 | 嵌入式 SDK | 不一致——不同代码路径 |
| Self-Host 官方主仓 | MemTensor main Dockerfile 模板 | 不一致——同样滚动更新 |
| **NAS 上 Krolik** | 比 c2bc36b15f 早的 main + Krolik 壳 | **你这条线** |

**经验**:跨实例迁移代码时,不要在 Krolik 上验证过的逻辑直接搬过去,必须重新在本机 / Cloud / 新实例上跑回归。

## 五、复现验证

```bash
# 健康检查
curl -s http://192.168.1.2:8001/admin/health
# 期望: {"status":"ok","auth_enabled":true,"master_key_configured":true}

# 端到端冒烟
python C:/Users/HMSJ/AppData/Local/Temp/memos_e2e_20260826/smoke2.py
# 期望: OK=7 FAIL=0,exit=0
```

如果 FAIL > 0,可能是 Krolik 行为又变了(主仓 main 演进 / 镜像升级)——重新跑一遍 §二 的"确证 base commit"流程,定位是 Krolik 改了还是上游改了。
