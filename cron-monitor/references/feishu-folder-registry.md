# 飞书 folder 监控与登记范式（2026-09-08 实战）

## 触发场景

- 用户说"X 项目飞书共享文件夹里有 N 份文档，记清楚都是干啥的"
- 用户说"共享文件夹里文档会不断更新增删"
- 任何"飞书 folder token → 列全树 → 写台账 → 给后续 cron prompt 当基线"任务

## 范式：5 步法

### Step 1：定位真 folder token

**坑**：飞书云空间有 2 个疑似根目录——
- `nodcnhTHWMNkwyj2RhEd0liu20e`（Hermes 默认根，往往是空的"素材/参考图"目录）
- 用户项目 folder（形如 `GSBqfMudlluQcYd7xbScMoOVnbd`，**用户主动分享才出现**）

**判定**：如果用户给了 folder URL（`/drive/folder/<token>`）就**直接用这个 token**，别去根目录里找。根目录只能列"我的云空间"里的内容，看不到"被分享给我"的 folder。

### Step 2：列全树（递归到底）

```bash
# 第一层
lark-cli drive files list --as bot --page-size 200 \
  --folder-token <folder_token> \
  | python3 -c "
import sys, json
d = json.load(sys.stdin)
files = d.get('data', {}).get('files', [])
for f in files:
    if f.get('type') == 'folder':
        print(f.get('token'), f.get('name'))  # 拿到所有子 folder token
"
```

**关键**：必须**递归列子 folder**——只看根目录会漏 80% 文档（伏妖记这次实测：根 2 个 docx + 5 子 folder；递归到底 = 19 份文档）。

### Step 3：每份文档 fetch 首段 + 元数据

```bash
# 每份 docx 单独 fetch（folder 列表只给元数据）
for tk in <token1> <token2> ...; do
  lark-cli docs +fetch --doc "$tk" --doc-format markdown --detail simple --as bot
done
```

**提取三件事**（用 regex）：
- `<title>` 标签里的文档名（vs 文件夹列表给的"name"，可能不一致）
- `<revision_id>`（判断是不是同一份文档的不同版本）
- 去掉 XML 标签后的纯文本字符数

### Step 4：写台账到 Projects/<项目>/文档台账.md

**结构范式**（不要直接抄，但骨架）：
```markdown
# <项目> · 飞书云文档台账

> 飞书为正本，本台账为登记镜像。

## 飞书 folder
- folder token: <token>
- 盘点方式: `lark-cli drive files list --folder-token <token> --as bot --page-size 200`
- 基线日期: YYYY-MM-DD

## 当前正本（主线打磨对象）
| 文档 | token | rev | 字符 | 用途 |

## <子目录名>/ 子目录（folder <token>）
... 递归列 ...

## 增删台账
每次盘点新增一节：YYYY-MM-DD 基线 / YYYY-MM-DD 差异
```

### Step 5：标记"角色身份"和"已废"

**关键**（这次实战栽过的坑）：
- 同一个项目可能有 3 份名字相似的 docx（剧本/项目台账/Hermes版），rev 完全不同
- **必须每份标"用途"**——"主线正本/项目台账/旧版作废/上游素材/美术考据/测试文档"
- 旧版本（last_status=ok 但 prompt 引用已废 token）必须**单独标"已废"**，别混在"正本"里
- 测试文档（字符数 <100 + 内容是"测试 bot 身份创建验证"）必须**单独标"别当素材用"**

## 配套铁律

1. **不要靠记忆维护 token 表**——每次盘点必重拉 folder
2. **MEMORY/OV 里"对象身份"声明必须有基线日期 + 失效条件**——"剧本正本 K5d3... 截至 2026-09-08（被替代时同步此条）"
3. **folder 列表 ≠ doc 内容**——folder 列表只给名字/token/mtime，**正文必须 fetch 才知道是不是"正本"**
4. **bot 身份能列、user 身份缺 scope 会 401**——伏妖记 folder 全树用 bot 列表（user 缺 `space:document:retrieve`）
5. **folder 结构变更（新增/删除 folder_token）= 必触发 cron prompt 审查**——否则像这次"修了 token 但 folder 结构还停在 8 月份"

## 验证清单（disk 三件套）

```bash
# 1. 台账文件实际写盘了
stat -c '%y %s %n' "Projects/<项目>/文档台账.md"

# 2. 核心 token 命中
grep -c "<正本 token>" "Projects/<项目>/文档台账.md"

# 3. 文件体积合理（应有 N KB，不是几字节）
wc -c "Projects/<项目>/文档台账.md"
```

## 反例（这次栽过的）

- ❌ 只列根目录 → 漏 18/19 份文档
- ❌ 用 user 身份列 → 401 unauthorized
- ❌ 看 folder 列表的 `name` 当文档用途 → 同名文件分不清哪个是"主线"
- ❌ 不实测 fetch → 把"杨编精撰独立版"当"主线"（伏妖记 cron 跑了 39 次都错的根因）
- ❌ 不标"已废" → 旧版本 token（EsMD/NSZK）跟新版本（K5d3/QO4y）混淆

## 关联资源

- `scripts/cron-prompt.md`（cron-monitor skill）：prompt 模板
- `cron-monitor/SKILL.md`「cron 配置审查范式」：cron prompt 引用了飞书 token 时的审查流程
- MEMORY「patch/write_file 写入铁律」：disk 三件套验证（stat mtime + grep 锚点 + wc 字节数）
