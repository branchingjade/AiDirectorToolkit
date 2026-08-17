# DSH 已知踩坑清单

> **来源标注**：以下全部提炼自 Cavan-Ou/hermes-dsh-collab 作者实测管线（style-museum，14 天 30 commits，REPORT.md 三自测全过）与项目文档，**非本机实测**。本机使用前先跑小任务验证。每条格式：症状 → 根因 → 对策。

## 模型 patch

1. **patch 整段替换语义（非深合并）**
   - 症状：`--patch` 只写局部字段（如 `reasoning: max`）→ `Provider is not configured: <provider>`
   - 根因：patch config 是整段替换；局部字段把 profile 里完整 provider 定义整个顶掉
   - 对策：每个 patch 自包含完整 provider 定义（displayName/apiKeyEnv/api/baseURL/models）

2. **qwen3.7-plus 不支持 reasoning: max**
   - 症状：vision patch 带 `reasoning: max` → `UNSUPPORTED_REASONING_EFFORT`
   - 对策：视觉模型不配推理档；靠声明 `input: [text, image]` 让 read_image 自动路由

3. **vision patch 不改 agent-default-model**
   - 对策：主模型保持 flash/pro；providers 里声明 qwen3.7-plus 带 `input: [text, image]` 即可
   - 验证姿势（换模型双确认）：①`dsh --patch <patch> "只输出你的主模型 id"` ②真任务跑通质量门

## 写回与沙箱

4. **写回靠启动目录**
   - 症状：dsh 产物落在 /tmp，项目里看不到
   - 根因：workspace-write 沙箱写权限 = 启动工作目录 + 平台临时根
   - 对策：派单命令必须 `cd <项目根> && dsh --profile headless "..."`

5. **bash 沙箱要 bubblewrap（Linux）**：宿主机没装 bubblewrap 沙箱拒绝写命令；Windows 上要么 WSL 要么绕沙箱

## git 纪律

6. **dsh 会自行 git commit**
   - 症状：执行者悄悄 commit（历史作者为 dsh 身份）
   - 根因：任务书未写明禁止
   - 对策：任务书执行纪律必须含「不 commit：git 唯一写者 = Hermes 主控」条款

## 进程与会话

7. **旧后端进程残留 → 假绿**
   - 症状：改完代码测试「全绿」却验到旧代码（nohup 被 guard 拦截、pkill 未执行）
   - 对策：主控用 terminal(background=true) 管进程，不用 nohup；验证前确认端口跑的是新代码

8. **headless 无 resume**：每次调用随机 session UUID——回炉 = 把失败原因写进新任务书重派（新会话），不是 resume；同阶段重试 >2 次升级链（dsh → Codex → 人工）

9. **任务书塞太满**：项目背景/历史教训整段贴进任务书浪费上下文——spec 只留本阶段最小信息，背景让 dsh 自己读项目 AGENTS.md/观测卡（必读清单列路径）

## 插件安装（bundle 形态）

10. `dsh plugin --profile X add <pkg>` 走 pnpm 转发（pnpm 要在 PATH）；`pnpm add` 只装依赖不激活——必须 dsh plugin add 注册进 profile bundles；装前备份 profile
11. **纯提示词 skill 别走 bundle**（pnpm 依赖解析对零代码资产纯增风险），复制目录到 `<skills root>/<name>/SKILL.md` 即可（只扫一层，热加载）
12. skill 写法对齐官方 `.agents/skills`：frontmatter name kebab-case 且与目录名一致；description 以「当……时使用」开头；SKILL.md=判断指引（阻断项→判断表格→What NOT to do 节→自测节），references/ 按需加载
