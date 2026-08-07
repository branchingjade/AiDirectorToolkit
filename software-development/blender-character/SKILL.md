---
name: blender-character
description: Blender 角色与动画管线——MB-Lab生成、Mixamo动作、Mixamo Rig插件、白模转换、插件兼容修复。触发词：MB-Lab、Mixamo、角色、人物、假人、白模、动画、动捕、blender character。
version: 1.0.0
---

# Blender 角色与动画管线

## 核心理念

**能用现成的就不要手写 bpy 搭。** 代码生成的几何体（球+柱、程序化管状）外观永远不如专业工具。优先顺序：Mixamo 现成角色 > MB-Lab 生成 > bpy 手搭。

## 角色来源

### Mixamo（首选）

- 网址: https://www.mixamo.com/
- 免费 Adobe 服务，需登录
- 内置数十个预绑定角色 + 2500+ 动捕动作
- FBX 导出，Blender 内建导入器直接可用
- **无需任何额外的生成工具**

### MB-Lab（备选，需要特定人种/体型时用）

- GitHub: https://github.com/animate1978/MB-Lab
- 安装方式：下载 zip → 解压到 addons → 启用
- 角色类型: `f_af01`(非裔女) `f_as01`(亚洲女) `f_ca01`(白人女) `m_as01`(亚洲男) 等
- 设置角色类型: `bpy.context.scene.mblab_character_name = 'm_as01'`
- 初始化: `bpy.ops.mbast.init_character()`

## 关键插件

### Mixamo Rig（必装）

- Blender Extensions 官方商店: https://extensions.blender.org/add-ons/mixamo-rig/
- GitHub: https://github.com/tdw46/mixamo_blender4-main
- v1.2.2，2个月前更新，54979下载，5星
- 功能：一键将 Mixamo FBX 骨架转为 IK 控制绑定 + 动画烘焙
- 免费 GPL v3

### BlenderKit（推荐）

- 在线资产库，数千免费模型/材质/HDR
- 安装：从 GitHub Releases 下载 zip → 解压到 addons → 启用

## 陷阱与修复

### MB-Lab Blender 5.1 兼容性

MB-Lab 在 Blender 5.1 上有两个已知崩溃点，需手动修复 `humanoid.py`：

**修复1: `get_subd_visibility` / `set_subd_visibility`（line 545-554）**
```
# 原代码直接用 obj.modifiers，obj 可能为 None
def get_subd_visibility(self):
    obj = self.get_object()
    if obj is None:          # ← 加这行
        return False          # ← 加这行
    ...
def set_subd_visibility(self, value):
    obj = self.get_object()
    if obj is None:          # ← 加这行
        return                # ← 加这行
    ...
```

**修复2: `update_character`（line 756）**
```python
def update_character(self, ...):
    obj = self.get_object()
    if obj is None:                              # ← 加这行
        logger.warning("object not found")        # ← 加这行
        return                                    # ← 加这行
    ...
```

### MB-Lab 角色类型不生效

症状：设置 `mblab_character_name = 'm_as01'` 后仍生成女性角色。

原因：`bpy.data.objects` 中残留旧角色数据（骨架、网格），`start_lab_session()` 检测到已有角色会复用。

修复：生成前彻底清空：
```python
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
for mesh in list(bpy.data.meshes): bpy.data.meshes.remove(mesh)
for arm in list(bpy.data.armatures): bpy.data.armatures.remove(arm)
```

### MB-Lab 白模转换

MB-Lab 材质使用纹理节点（albedo.png, bump.png 等）覆盖 BSDF Base Color。仅改 Base Color 无效。

正确做法：**删除所有 TEX_IMAGE 节点 + 断开所有 BSDF 输入连接**：
```python
for slot in char.material_slots:
    mat = slot.material
    if mat and mat.use_nodes:
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        bsdf = None
        for node in list(nodes):
            if node.type == 'BSDF_PRINCIPLED': bsdf = node
            elif node.type == 'TEX_IMAGE': nodes.remove(node)
        if bsdf:
            for inp in bsdf.inputs:
                for link in list(links):
                    if link.to_socket == inp: links.remove(link)
            bsdf.inputs["Base Color"].default_value = (0.70, 0.70, 0.70, 1)
            bsdf.inputs["Roughness"].default_value = 0.50
```

### Cats Blender Plugin 不推荐

- GitHub: absolute-quantum/cats-blender-plugin
- 最后代码提交 2024-05，已停止维护
- 主要用于 VRChat 模型优化（减面/合并材质），非通用 Mixamo 工具
- Blender 5.1 需修复 `addon_support` 枚举去掉 `TESTING`

## 完整工作流

```
Mixamo 网站 → 选角色 → 搜动作(crouch/lean/walk) → 下载FBX
    ↓
Blender File → Import → FBX
    ↓
N面板 → Mixamo Rig → 一键 IK
    ↓
场景中使用
```

如需定制角色体型/人种 → MB-Lab 生成 → 导出 FBX → Mixamo 自动绑定 → 同上流程。
