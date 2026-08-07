# Blender 免费插件安装记录

**最后更新：2026-07-02**

## MB-Lab（角色生成器）

- 来源：GitHub `animate1978/MB-Lab`
- 安装方式：下载 master.zip → 解压到 Blender user addons → 启用
- 生成角色：`bpy.ops.mbast.init_character()` → `bpy.ops.mbast.finalize_character()`
- 输出：18210 顶点高质量人体 + 皮肤纹理 + 骨骼绑定
- 内置操作符：`bpy.ops.mbast.*`（init_character, finalize_character, character_generator, 等）

```python
# 一键生成 MB-Lab 角色
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete()
bpy.ops.mbast.init_character()
bpy.ops.mbast.finalize_character()
# 角色命名为 f_af01 (MESH) + f_af01_skeleton (ARMATURE)
```

## BlenderKit（在线素材库）

- 来源：GitHub `BlenderKit/BlenderKit` releases（**不要用 master 分支**）
- 最新版本：v3.21.0.260628（2026-07-02）
- 安装方式：下载 release .zip → 解压到 Blender user addons 目录 → 启用
- 功能：N 键打开面板，免费注册后搜索数千免费 3D 模型/材质/HDR
- Python 安装：
  ```python
  url = "https://github.com/BlenderKit/BlenderKit/releases/download/v3.21.0.260628/blenderkit-v3.21.0.260628.zip"
  # 下载→解压→复制到 bpy.utils.script_path_user()/addons/blenderkit
  bpy.ops.preferences.addon_enable(module="blenderkit")
  ```

## 内置插件（Blender 5.1 需手动启用）

⚠️ Blender 5.1 改用 **Extensions 系统**，以下插件不在传统 addons 目录，需通过 **Edit → Preferences → Get Extensions** 面板搜索启用：

## Mixamo Rig（Mixamo FBX → IK 控制绑定）

- 来源：Blender Extensions 官方商店 `extensions.blender.org/add-ons/mixamo-rig/`
- 开发者：tyler.tofu / tdw46（GitHub: `tdw46/mixamo_blender4-main`）
- 版本：v1.2.2，2026年6月更新，54979 次下载，5星（6评）
- 许可：GPL v3.0，免费
- 基于 Adobe 官方已停更的 Mixamo Addon 升级
- 兼容：Blender 4.2 LTS（5.1 实测可用）
- 功能：一键从 Mixamo FBX 骨架生成 IK 控制绑定 + 动画烘焙 + IK/FK 切换
- 安装方式：GitHub 下载 main.zip → 解压到 addons → 启用模块 `mixamo_rig`

## ~~Cats Blender Plugin~~（已弃用）

- 最后代码提交：2024-05-28（超过两年未更新）
- 本质是 VRChat 优化工具（减面/合并材质），对 Mixamo→Blender 工作流非必需
- 不再推荐安装
