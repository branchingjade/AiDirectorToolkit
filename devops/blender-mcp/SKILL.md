---
name: blender-mcp
description: Blender MCP 集成——安装、配置、版本选择（官方vs社区）、Llama.cpp本地LLM驱动、多版本共存。触发词：blender mcp、blender_mcp、Blender AI、blender LLM、MCP Blender。
version: 1.3.0
---

# Blender MCP

## 概述

blender_mcp 让 LLM 通过 MCP 协议操控 Blender。两个组件通过 TCP socket 通信：

```
LLM客户端 ⇐ MCP/stdio ⇒ blender-mcp (Python) ⇐ TCP(9876) ⇒ Blender 插件
```

**必装**：MCP Server + Blender 插件。CLI 聊天客户端（`chat_client/`）是可选的调试前端。

---

## 两版本速查

| 维度 | 官方版（lab/blender_mcp） | 社区版（ahujasid/blender-mcp） |
|------|--------------------------|-------------------------------|
| 维护者 | Dalai Felinto（Blender 基金会） | Siddharth Ahuja（独立开发者） |
| 许可证 | **GPL-3.0**（商用注意传染性） | **MIT** |
| PyPI 包名 | 同名 `blender-mcp`，需 git 安装 | `pip install blender-mcp` |
| Python 包 | `blmcp` | `blender_mcp` |
| Blender 插件名 | `blender_mcp_addon` | `Blender MCP`（`addon.py`） |
| 默认端口 | `localhost:9876` | `localhost:9876` |
| 本地 LLM | 🟢 Llama.cpp 一级支持 | 🟡 可用但不优先 |
| AI 3D 生成 | ❌（可通过 execute_blender_code 自行调用） | 🟢 Poly Haven / Hyper3D / Hunyuan3D |
| 无头模式 | 🟢 `_for_cli` 系列工具 | ❌ |
| 内置文档 | 🟢 Blender API + 用户手册 RST | ❌ |
| 最新版 | v1.0.0（2026-04-27） | v1.6.4（PyPI） |

详细对比见 `references/versions-comparison.md`。

Rigify 人体角色创建流程见 `references/rigify-character-workflow.md`。3D 资产渠道费用对比见 `references/asset-pricing.md`。场景搭建可复用代码模板见 `references/scene-building-patterns.md`。免费角色/资产插件安装记录见 `references/blender-plugins.md`。MB-Lab 安装/修复/用法见 `references/mblab-setup.md`。Kimodo Blender Bridge 见 `references/kimodo-blender-bridge.md`。Mixamo 动作工作流及插件对比见 `references/mixamo-workflow.md`。

---

## 官方版安装

```bash
# MCP Server（必须 git 安装，PyPI 包是社区版）
pip install git+https://projects.blender.org/lab/blender_mcp.git#subdirectory=mcp

# Blender 插件：添加 Lab Extensions 仓库 https://lab.blender.org/
# → Edit > Preferences > Extensions → 搜索 MCP → 安装启用
```

## 社区版安装

### MCP Server

```bash
pip install blender-mcp
```

### Blender 插件部署

社区版插件是单个 `addon.py`，需部署到 Blender 用户 addons 目录：

**Windows**:
```powershell
# Blender 5.1 用户 addons 路径
$path = "$env:APPDATA\Blender Foundation\Blender\5.1\scripts\addons\blender_mcp_community\"
mkdir -p $path
cp addon.py $path\__init__.py
```

**macOS**:
```bash
mkdir -p ~/Library/Application\ Support/Blender/5.1/scripts/addons/blender_mcp_community/
cp addon.py ~/Library/Application\ Support/Blender/5.1/scripts/addons/blender_mcp_community/__init__.py
```

**Linux**:
```bash
mkdir -p ~/.config/blender/5.1/scripts/addons/blender_mcp_community/
cp addon.py ~/.config/blender/5.1/scripts/addons/blender_mcp_community/__init__.py
```

部署后在 Blender 中：Edit → Preferences → Add-ons → 搜 "Blender MCP" → 勾选启用。

### Hermes MCP 配置

使用 `hermes mcp add`（不是 `config.yaml` 的 `mcp_servers`，后者不会被 `hermes mcp list` 识别）：

```bash
# 推荐方式：使用包装脚本（见下方）
hermes mcp add blender-mcp \
  --command "C:\Users\<user>\AppData\Local\Programs\Python\Python312\python.exe" \
  --args "-s" "-E" "<path-to>/blender-mcp-wrapper.py"
```

添加时会依次提示：Overwrite? → Enable all tools? 需用 `printf 'y\ny\n'` 管道应答。

Hermes MCP 依赖 `mcp` Python SDK，Hermes venv 无 pip（uv 管理），需用：
```bash
uv pip install --python ~/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe "hermes-agent[mcp]"
```

### Windows 包装脚本（推荐：`blender-mcp-wrapper.py`）

直接用 `.cmd` 脚本有两个问题：
1. **PYTHONPATH 污染**：Hermes venv 的 pydantic 被系统 Python 的 mcp 误导入
2. **UTF-8 编码错误**：Windows 中文错误信息（`由于目标计算机积极拒绝...`）是 GBK 编码，Hermes MCP 客户端只接受 UTF-8

包装脚本解决两个问题——清环境变量 + 强制 UTF-8 输出。见 `scripts/blender-mcp-wrapper.py`。

---

## Llama.cpp 本地 LLM 集成

参见 `references/llama-cpp-setup.md`（完整步骤）。核心流程：

```bash
# 1. 装 Llama.cpp
winget install llama.cpp          # Windows
brew install llama.cpp            # Mac

# 2. 下载模型（推荐 Gemma4-26B 或 Qwen3.6-35B，GGUF 量化）
# 3. 启动 llama-server
llama-server -m <模型路径.gguf>

# 4. 启动 blender-mcp HTTP 模式
uv --directory <clone路径>/mcp run blender-mcp --transport http --port 9191

# 5. 在 Llama.cpp Web UI (http://127.0.0.1:8080) → MCP Servers → 添加
#    http://127.0.0.1:9191/
```

---

## 两版本共存

三个冲突点，均可解决：

| 冲突 | 解决 |
|------|------|
| PyPI 包同名 `blender-mcp` | 用不同 venv，或一个 git 安装一个 pip 安装 |
| CLI 命令同名 | 不同 venv 隔离激活 |
| 默认端口 9876 | 在 Blender 插件偏好里把其中一个改成 9877 |

**Blender 插件层面不冲突**（官方 `blender_mcp_addon` vs 社区 `Blender MCP`），两个插件可共存。

---

## 选版指南

| 场景 | 推荐 |
|------|------|
| 完全本地化 + 开源模型 | 官方版（Llama.cpp 原生支持） |
| Claude Desktop + 功能丰富 | 社区版（开箱即用，AI 3D 生成） |
| 商用项目 | 社区版（MIT，无 GPL 传染风险） |
| 后台/无头批量处理 | 官方版（`_for_cli` 工具） |
| 已有 Resolve MCP，统一管线 | 两个都能接 Hermes |

---

## Windows Hermes 集成

### MCP 服务器注册

**必须用 `hermes mcp add`，不能只写 `config.yaml`**：

```bash
hermes mcp add blender-mcp --command cmd.exe --args /c "C:\Users\<user>\Documents\Hermes\scripts\blender-mcp.cmd"
```

`config.yaml` 中的 `mcp_servers` 段是旧格式，Hermes 不会自动加载。用 `hermes mcp list` 验证。

### Python 路径污染

Hermes venv 的 `PYTHONPATH` 环境变量会被系统 Python 继承，导致 `blender-mcp`（装于系统 Python312）import 到 Hermes venv 的 `mcp`/`pydantic` 包，版本不兼容报错。

**解决**：创建 wrapper 脚本清除环境变量并强制 UTF-8：

```python
# blender-mcp-wrapper.py
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
if 'PYTHONPATH' in os.environ: del os.environ['PYTHONPATH']
from blender_mcp.server import main
main()
```

然后 `hermes mcp add` 指向 wrapper。

### 中文编码问题

Windows 中文系统的 cmd.exe 输出 GBK 编码，会导致 Hermes MCP 客户端 UTF-8 解码失败。wrapper 中的 `TextIOWrapper` 修复 + Python `-s -E` 标志避免环境变量干扰。

### Hermes MCP 依赖安装

Hermes 的 uv 管理 venv 没有 pip，必须用 `uv pip install`：

```bash
uv pip install --python ~/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe "hermes-agent[mcp]"
```

## MCP Server 配置（Windows）

社区版 MCP Server 需通过 Hermes `mcp add` 注册。Windows 上 `cmd.exe` 管道有 UTF-8 编码问题，**必须用 Python wrapper 脚本**：

```bash
hermes mcp add blender-mcp --command "C:\\Users\\<user>\\AppData\\Local\\Programs\\Python\\Python312\\python.exe" --args "-s" "-E" "<wrapper路径>"
```

Wrapper 脚本（`scripts/blender-mcp-wrapper.py`）需做三件事：
1. `sys.stdout/stderr` 强制 UTF-8（避免 Windows 中文错误信息导致 MCP 解码失败）
2. 删除 `PYTHONPATH` 环境变量（避免 Hermes venv 包污染系统 Python 的 import）
3. 调用 `from blender_mcp.server import main; main()`

**常见失败**：
- `'utf-8' codec can't decode byte 0xb0` → 没设 UTF-8 wrapper，stderr 有中文字符
- `Connection closed` → PYTHONPATH 污染或导入错误
- 找不到 `blender_mcp` 模块 → 需先 `pip install blender-mcp` 到系统 Python

## Hermes MCP 依赖

blender-mcp MCP Server 需要 Hermes venv 里有 `mcp` 包。Hermes 的 venv 是 uv 管理的，**不能**用系统 `pip`：

```bash
uv pip install --python ~/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe "hermes-agent[mcp]"
```

## Rigify 程序化创建

Rigify human meta-rig 不能用 `bpy.ops.object.armature_human_meta_rig_add`（Blender 5.1 不存在此操作符）。正确方法：

```python
from rigify.metarigs import human

bpy.ops.object.armature_add(location=(0,0,0))
arm = bpy.context.object
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.armature.select_all(action='SELECT'); bpy.ops.armature.delete()
human.create(arm)    # ← 关键：直接调用 human.create(armature_object)
bpy.ops.object.mode_set(mode='OBJECT')
# 生成控制器
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.pose.rigify_generate()
```

## MB-Lab 集成

详见 `references/mblab-setup.md`。

**安装**：从 GitHub master 分支下载 zip，解压到 Blender user addons 目录，启用模块 `MB-Lab-master`。

**关键操作**：
- **选择角色类型**：必须设置 `bpy.context.scene.mblab_character_name`，否则默认女性
- **数据残留**：`bpy.data.objects` 中的旧数据会导致角色类型复用。生成新角色前必须清空 `bpy.data.objects` + `bpy.data.meshes` + `bpy.data.armatures`
- **Blender 5.1 兼容**：`humanoid.py` 的 `get_subd_visibility()` 和 `update_character()` 缺少 None 检查，需手动 patch

**白模转换**：MB-Lab 使用纹理节点（albedo/bump/melanin 等）覆盖 Base Color。必须删除 TEX_IMAGE 节点并断开所有 BSDF 输入连线。详见 references 文件。

## Voxel Remesh 融合几何体

用球+柱拼人体后，Voxel Remesh 可以融合成连续曲面。**关键**：部件必须重叠，否则 Remesh 只保留最大块。

- 关节球半径放大 30%（1.3×）确保与肢体圆柱重叠
- `remesh.mode = 'VOXEL'`，`voxel_size = 0.012`（人体 1.75m 尺度）
- 融合后顶点数应从 900+ 增加到 1000+（说明在融合而非丢弃）

## 用户交互原则

- **全自动化优先**：所有操作通过代码完成，不要求用户手动步骤
- **先规划再搭建**：场景搭建前先备文字方案
- **白模优先**：角色用纯白/灰无纹理材质
- **坐标验证构图**：打印物体坐标确认空间关系，不用视觉截图——视觉模型对 Blender 视口的左右/空间解读极不稳定
- **优先找现成工具**：用户明确偏好用已有插件/工具而非手写 bpy 代码。需要好看角色→MB-Lab，需要动作→Mixamo，不要反复迭代代码生成方案

## MCP 上下文陷阱

- `bpy.ops.wm.open_mainfile()` 会重置 Blender 上下文，导致后续 `bpy.context.screen.areas` 为 None，MCP 连接中断。**不要在 MCP 脚本中调用此操作符**——改为让用户手动打开文件，或在一个脚本中完成所有操作后保存。
- `convert(target='MESH')` 前确保 `bpy.context.object` 存在（metaball 对象未被意外删除）
- 删除对象后用 `bpy.data.objects.remove(obj, do_unlink=True)` 彻底清除，而不仅是场景删除
- 批量删除时用 `list(bpy.data.objects)` 拷贝迭代，避免 `dictionary changed size` 错误

## 视觉验证陷阱

**不要用截图+视觉分析验证 Blender 3D 构图**。视觉模型对 Blender 视口的左右/空间解读极不稳定：
- 同一场景，同一摄像机角度，两次截图可能得到相反的"左/右"判断
- 材质预览模式 vs 实体模式显示效果截然不同
- 骨架/控制器会遮挡皮肤网格

**正确验证方式**：打印物体坐标 → 计算空间关系 → 保存 .blend → 用户在 Blender 中审阅。坐标不会骗人，视觉分析会。

## Kimodo AI 动作生成

Kimodo Blender Bridge 是 AI 驱动的 3D 动作生成插件：文字描述 → Kimodo 模型 → SOMA 骨架动画 → Blender 场景 → 重定向到任意角色骨架。

详见 `references/kimodo-blender-bridge.md`。

安装：zip 解压到 Blender addons → 启用 → N 面板 Kimodo → Install Kimodo (Auto)（自动装 PyTorch + 模型）。

## 插件推荐（免费）\n\n| 插件 | 用途 | 安装方式 |\n|------|------|---------|\n| **MB-Lab** | 参数化人物生成（男女/年龄/体型） | GitHub zip → addons |\n| **BlenderKit** | 在线素材库（模型/材质/HDR） | GitHub Releases zip → addons |\n| **Mixamo Rig** | Mixamo FBX → IK 控制绑定（替代已停更的 Adobe 官方插件） | Blender Extensions 商店 / GitHub `tdw46/mixamo_blender4-main` |\n| **LoopTools** | 网格编辑工具 | Blender 内置启用 |\n| **A.N.T. Landscape** | 地形生成 | Blender 内置启用 |\n| **Node Wrangler** | 节点编辑加速 | Blender 内置启用 |\n\n> ~~Cats Blender Plugin~~ 已弃用（2024-05 最后代码），对 Mixamo 场景非必需。不要安装。

## 3D 资产管理（Eagle MCP）

Eagle 是本地素材管理工具（API 端口 41595）。通过 Eagle MCP 可程序化管理 3D 资产：

```bash
# 配置（npm 包，npx 运行）
hermes mcp add eagle --command npx --args -y eagle-mcp-server
```

13 个 MCP 工具：`createFolder`、`addItemFromPath`、`addItemsFromPaths`、`updateItem`（标签/注释）、`listItems`、`searchItems` 等。

建议 Eagle 目录结构：`素材库/三维/角色/`（.blend）、`素材库/三维/动作/`（Mixamo FBX）、`素材库/三维/场景/`、`素材库/三维/HDR/`。

## 帧率统一

**所有 Blender 项目统一 30 FPS**——Kimodo 硬限制且 Mixamo 默认输出 30fps。`bpy.context.scene.render.fps = 30`。

## 角色动画双管线

Kimodo 固定 30fps 生成动作，Bridge 自动做帧率映射到场景。建议场景统一设为 30fps。

**常规动画优先用 Mixamo**（2500+ 专业动捕，FBX Binary → `mr.make_rig()` → 一键IK）。Mixamo 搜不到的精确用 Kimodo 生成。

**Mixamo Rig 只兼容 Mixamo 骨架**：要求骨骼前缀为 `mixamorig:`。MB-Lab 骨架（`root` 前缀）、Rigify 骨架均不兼容。不要对非 Mixamo 来源的角色执行 `bpy.ops.mr.make_rig()`。

**⚠️ `mr.make_rig()` 必须选中骨架，不是身体网格**：选中 MESH 身体会报 `poll() failed, context is incorrect`。正确做法：

```python
# ❌ 选中身体 → poll() failed
body = bpy.data.objects['男']
bpy.context.view_layer.objects.active = body

# ✅ 选中骨架
arm = bpy.data.objects['男_骨架']
bpy.ops.object.select_all(action='DESELECT')
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.mr.make_rig()
```

**应用 Mixamo Rig 后导出干净 FBX**（排除控制形状 cs_*）：

```python
# 只选身体+关节+骨架，排除 cs_ 控制形状
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.data.objects:
    if obj.type in ('MESH', 'ARMATURE') and not obj.name.startswith('cs_'):
        obj.select_set(True)
bpy.ops.export_scene.fbx(filepath=out, use_selection=True, add_leaf_bones=False, bake_anim=False)
```

用 `use_selection=True` 而非 `use_selection=False`——全场景导出会带上 Mixamo Rig 生成的 20+ 个控制形状物体。

**Mixamo FBX 清理**（移除动画保留默认姿势）：
```python
# 导入 FBX → 清除 actions → 导出干净 FBX
bpy.ops.import_scene.fbx(filepath=path)
for action in list(bpy.data.actions):
    bpy.data.actions.remove(action)
for obj in bpy.data.objects:
    if obj.animation_data:
        obj.animation_data_clear()
bpy.ops.export_scene.fbx(filepath=out, bake_anim=False, add_leaf_bones=False)
```

**bpy 控制 Kimodo**（仅英文 prompt，中文会产生乱码）：
```python
s = bpy.context.scene.kimodo
s.prompt = "a worker crouches against a wall"  # 英文 prompt
s.duration = 5.0  # 秒
s.seed = 42
bpy.ops.kimodo.generate()
# 成功后 Kimodo_Source 骨架 + 动画出现在场景中
```
6. **bpy 代码无法生成好看的人体网格**——球+柱、Metaball、Voxel Remesh 等程序化方法的天花板很低。需要好看的角色外观时，引导用户下载 CC0 模型或手动建模，不要反复迭代代码生成。
7. **Sketchfab/Hyper3D/Hunyuan3D 需要额外配置**——`search_sketchfab_models` 等命令可能返回 "Unknown command type"，说明 Blender 插件未配置对应 API key。
   ```bash
   hermes mcp add blender-mcp --command "C:\Users\HMSJ\AppData\Local\Programs\Python\Python312\python.exe" --args "-s" "-E" "C:\Users\HMSJ\Documents\Hermes\scripts\blender-mcp-wrapper.py"
   ```
   wrapper 脚本 `scripts/blender-mcp-wrapper.py` 做了两件事：①清除 PYTHONPATH/PYTHONHOME ②强制 stdout/stderr 为 UTF-8（避免 Windows GBK 编码报错）。Blender 插件部署在 `%APPDATA%\Blender Foundation\Blender\5.1\scripts\addons\blender_mcp_community\__init__.py`。
5. **Llama.cpp 的 OpenAI API 对 tool calling 不如原生 MCP 稳定**——优先用 MCP 直连而非 OpenAI 兼容层。
6. **Windows PYTHONPATH 污染**——Hermes venv 中的 pydantic 可能被系统 Python 的 mcp 包误导入，导致 `ModuleNotFoundError: pydantic_core._pydantic_core`。必须用包装脚本清环境变量后启动（`python -s -E wrapper.py`）。
7. **Blender 必须运行且插件已启用**——MCP Server 启动时若连不上 9876 端口，会报 `ConnectionRefusedError` 并退出。这是正常的：打开 Blender → 启用插件后重试即可。插件不随 Blender 启动自动启用，每次需手动确认。
8. **UTF-8 编码错误**——直接 `cmd.exe /c blender-mcp.cmd` 会导致 `'utf-8' codec can't decode byte 0xb0`。Windows 的中文错误信息是 GBK 编码，Hermes MCP 客户端只接受 UTF-8。用包装脚本（`sys.stdout/stderr = TextIOWrapper(..., encoding='utf-8', errors='replace')`）解决。
9. **Hermes MCP 添加的管道输入**——`hermes mcp add` 有两次交互确认（Overwrite? + Enable all tools?），需 `printf 'y\ny\n' | hermes mcp add ...` 一次应答两个。
10. **`--args` 必须是最后参数**——`hermes mcp add` 的 `--args` 是位置参数，必须放命令行末尾，否则报 `error: the following arguments are required: name`。
11. **中文 Blender 节点名不匹配**——中文版 Blender 的材质节点名称是本地化的（如 `原理化 BSDF` 而非 `Principled BSDF`），用字符串索引会 `KeyError`。**正确方式是按类型查找**：
    ```python
    def get_bsdf(mat):
        for node in mat.node_tree.nodes:
            if node.type == 'BSDF_PRINCIPLED':
                return node
        return None
    ```
    同样，世界背景用 `node.type == 'BACKGROUND'`。所有材质脚本都应优先用 `node.type` 匹配，避免硬编码中英文节点名。
12. **视口截图前必须切渲染模式**——默认 Solid 模式截图只有灰模。截材质/光照效果前：
    ```python
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'MATERIAL'  # 或 'RENDERED'
    ```
13. **场景搭建可复用模式**——见 `references/scene-building-patterns.md`（工具函数 + 小人 + 三方案模板）。
14. **摄像机视角切换**——截图前需确保视口用摄像机视角而非 User Perspective 模式。`bpy.ops.view3d.view_camera()` 在 MCP 环境中可能因 context override 失败，改用区域属性直接设置：
    ```python
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            space = area.spaces.active
            space.region_3d.view_perspective = 'CAMERA'
            break
    ```
    注意：使用 `region_3d` 而非 `rv3d`（后者不存在于 SpaceView3D）。
15. **远程构图局限性**——通过 MCP 截图验证 3D 场景构图效率极低。每轮需要"写代码→执行→截图→视觉分析→修正"的循环，且视觉模型对 Blender 视口的空间解读不稳定。**正确做法**：代码搭好场景骨架（物体位置、材质、光照），保存 .blend，让用户在 Blender 中直接调机位。机位用代码微调不如用户拖拽快。多方案对比时，每个方案保存独立 .blend，用户逐一打开审阅。
16. **Rigify 人体全流程**——`human.create(armature_obj)` 需要传入骨架对象而非 context。完整可动角色流水线（已验证在 MCP 中可行）：\n    ```python\n    from rigify.metarigs import human\n    # Step 1: 创建 MetaRig\n    bpy.ops.object.armature_add()\n    arm = bpy.context.object\n    bpy.ops.object.mode_set(mode='EDIT')\n    bpy.ops.armature.select_all(action='SELECT')\n    bpy.ops.armature.delete()\n    human.create(arm)  # 159 根骨骼\n    bpy.ops.object.mode_set(mode='OBJECT')\n    # Step 2: 生成控制器\n    bpy.ops.pose.rigify_generate()  # 706 根骨骼 + IK/FK/手指/面部\n    rig = bpy.context.object  # 名称: RIG-MetaRig\n    # Step 3: 创建皮肤网格（球体+圆柱拼接，T-Pose 对齐 MetaRig）\n    # ... 用 bpy.ops.mesh.primitive_* 逐个添加部件 ...\n    bpy.ops.object.join()  # 合并为单 mesh\n    skin = bpy.context.object\n    bpy.ops.object.shade_smooth()\n    # Step 4: 自动蒙皮（✅ 已验证有效）\n    skin.select_set(False)\n    rig.select_set(True)\n    bpy.context.view_layer.objects.active = rig\n    bpy.ops.object.parent_set(type='ARMATURE_AUTO')  # 自动权重绑骨\n    ```\n    **关键**：`parent_set(type='ARMATURE_AUTO')` 在 MCP 环境中可用，无需交互式绑定。皮肤网格部件用关节球+锥形柱拼接，关节处（肩/肘/腕/髋/膝/踝）用稍大球体标记，肢体用圆柱连接，合并后细分获得平滑效果。
17. **假人/角色创建策略**——场景中的可动人物有以下方案（优先级从高到低）：\n    a) **Rigify 骨架 + 关节球模型**：关节球+锥形肢体的美术人偶风格，用 `bpy.ops.mesh.primitive_*` 拼接后 `bpy.ops.object.join()` 合并。配合细分修改器获得平滑效果。适合程序化批量创建。\n    b) **Hyper3D Rodin 生成**：文生 3D，需 API key。`generate_hyper3d_model_via_text` 节点依赖 addon 是否配置 API key。\n    c) **Sketchfab 搜索**：`search_sketchfab_models` 需 API key，同上。\n    d) **Rigify 完整流程**：骨架→控制器→手动绑 skin mesh，在 MCP 中难以自动化。\n18. **物体批量删改**——`bpy.data.objects.remove(obj, do_unlink=True)` 比 `bpy.ops.object.delete()` 更可靠（不依赖 context）。删除时注意用 `list(bpy.data.objects)` 拷贝迭代，避免 `dictionary changed size` 错误。同样适用于 materials/cameras/lights。
19. **Voxel Remesh 重叠要求**——Voxel Remesh 只在几何体相互穿插时才能融合为连续表面。如果各部件仅接触而不重叠，顶点数不增反降（只保留了最大连通块）。特征：960v→256v=失败；960v→1260v=成功。让管状端点深入主体 20% 半径深度。
20. **`execute_code` 无 bpy**——Hermes 的 `execute_code` 运行在独立 Python 环境，`import bpy` 会 `ModuleNotFoundError`。所有 Blender 操作必须通过 `mcp_blender_mcp_execute_blender_code`。
21. **程序化人体外观天花板**——bpy 代码（球+柱、Metaball、Voxel Remesh、Skin Modifier、管状截面）生成的人体网格外观始终有限。需要好看角色时，优先用 MB-Lab（`bpy.ops.mbast.init_character()`）或让用户手动建模。不要反复迭代代码生成路线。MB-Lab 可通过 `bpy.context.scene.mblab_character_name = 'm_as01'` 全自动选择性别/类型，无需用户手动操作。详见 `references/mblab-setup.md`。\n21. **Rigify 程序化摆姿势**——生成控制器（RIG-MetaRig）后，通过 Pose 模式修改骨骼变换来摆姿势。**核心发现**：\n    - **IK 控制优先**：用 IK 控制器（`foot_ik.L/R` 位置、`torso` 位置+旋转）比 FK 控制器（`thigh_fk`、`spine_fk` 旋转）更可靠。FK 旋转可能因 Rigify 的 IK/FK 模式约束被覆盖。\n    - **控制器命名**：生成后的实际骨骼名与 MetaRig 不同。查名方法：\n      ```python\n      bpy.ops.object.mode_set(mode='POSE')\n      controls = [b.name for b in rig.pose.bones\n                  if not b.name.startswith(('DEF-','ORG-','MCH-','VIS-','WGT-'))]\n      ```\n      关键控制器：`torso`（整体移动+旋转）、`foot_ik.L/R`（IK脚控）、`head`、`neck`、`shoulder.L/R`、\n      `spine_fk`/`spine_fk.001`/`spine_fk.002`、`upper_arm_fk.L/R`、`forearm_fk.L/R`、\n      `hand_fk.L/R`、`thigh_fk.L/R`、`shin_fk.L/R`、`foot_fk.L/R`。\n      手指：`f_index.01_master.L`、`thumb.01_master.L` 等。\n    - **姿势应用方式**：\n      ```python\n      from mathutils import Vector, Euler\n      bpy.ops.object.mode_set(mode='POSE')\n      pb = rig.pose.bones\n      pb['torso'].location = Vector((0, 0, -0.2))  # 下移\n      pb['torso'].rotation_quaternion = Euler((0.3, 0, 0), 'XYZ').to_quaternion()  # 前倾\n      pb['foot_ik.L'].location = Vector((0, -0.05, -0.35))  # 脚向下移→膝弯曲\n      bpy.ops.object.mode_set(mode='OBJECT')  # 结束 Pose 模式\n      ```\n    - **姿势可视化**：MCP 截图可能仍显示 T-Pose（Rest Position），需确保 `rig.data.pose_position = 'POSE'` 且所有骨骼层 `rig.data.collections[].is_visible = True`。实际变形在文件中正确存储，用 Blender 打开即可看到。\n\n22. **场景搭建空间验证铁律**——不要通过截图+视觉分析验证 3D 构图。正确方式：\n    - 搭建前在脑中建立坐标系：X=左右（负=左）、Y=近远（正=近/前景）、Z=上下\n    - 搭建后打印关键物体坐标确认相对位置：\n      ```python\n      for name in ['Pillar','Gate','Camera']:\n          obj = bpy.data.objects.get(name)\n          if obj: print(f\"{name}: x={obj.location.x:.1f} y={obj.location.y:.1f} z={obj.location.z:.1f}\")\n      ```\n    - 摄像机 Track To 约束（`constraint.type='TRACK_TO'`）比手动计算 Euler 角更直观。\n    - 保存 .blend 让用户在 Blender 中直接审阅，比截图反馈快得多。 在 MCP 环境中可能因 context 问题失败（`poll() failed`），导致后续代码操作已失效的 RNA 结构（`StructRNA of type Object has been removed`）。当前不建议在 MCP 脚本中使用 metaball 转 mesh。\n20. **`hermes mcp add` 工具启用**——添加服务器时如果 \"Enable all 22 tools?\" 提示被管道提前消费（`echo y` 只应答了 \"Overwrite?\"），工具不会被启用。必须 `printf 'y\\ny\\n'` 或保存后手动 `hermes mcp configure blender-mcp` 启用。
