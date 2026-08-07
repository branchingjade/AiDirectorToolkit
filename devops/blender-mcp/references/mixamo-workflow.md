# Mixamo 动作工作流

## 概述

Mixamo (mixamo.com) 是 Adobe 的免费在线 3D 角色动画平台，提供：
- 2500+ 专业动作捕捉动画
- 自动角色绑定（上传 OBJ/FBX）
- 内置可下载角色（X Bot、Y Bot 等）
- FBX 导出含骨骼+动画

配合 **Mixamo Rig** Blender 插件（Blender Extensions 官方商店），从 Mixamo FBX 一键生成 IK 控制绑定。

## Mixamo Rig 插件

- 来源：Blender Extensions → 搜索 "Mixamo Rig"（开发者 tyler.tofu / tdw46）
- GitHub：https://github.com/tdw46/mixamo_blender4-main
- 版本：v1.2.2（2026 年活跃维护）
- 功能：选中 Mixamo FBX 导入的骨架 → 一键生成 IK/FK 控制器 → 动画烘焙
- 兼容：Blender 4.2+（5.1 实测可用）

### Mixamo Rig 面板

3D View → N 键 → Mixamo Control Rig：
- **Control Rig**：一键生成 IK 控制器
- **Animation**：Zero out / Bake / Import animation
- **Export**：GLTF 导出
- **IK/FK Snap**：手臂/腿 IK↔FK 切换

## 工作流

```
Mixamo 网站 → 选角色 → 搜动作 → 下载 FBX → Blender File→Import→FBX → N键→Mixamo Rig→生成IK
```

### 搜索动作关键词

| 场景需求 | 搜索词 |
|---------|--------|
| 蹲坐 | `sitting`, `crouch` |
| 站姿休息 | `idle`, `standing idle` |
| 靠墙 | `lean wall` |
| 走路 | `walking`, `walk forward` |
| 工作 | `working`, `carry` |

### 下载设置

- **Format: FBX Binary**（ASCII FBX 不被 Blender 支持！）
- FPS: 30（与 Kimodo 统一）
- Skin: With Skin（如需角色本身）

### Blender 导入后一键 IK

```python
# 选中导入的骨架（默认名 Armature）→ 生成 IK 控制绑定 + 动画烘焙
bpy.context.view_layer.objects.active = bpy.data.objects.get("Armature")
bpy.context.view_layer.objects.active.select_set(True)
bpy.ops.mr.make_rig()
# 输出：Control Rig Done! 含 IK/FK 手脚控制器 + 动画已烘焙
```

**全自动流程已验证**：FBX Binary 导入 → `mr.make_rig()` → 126帧动画 + IK 控制器 → 空格播放。WARNING 可忽略（fbx Short 属性不支持 + cs_user 形状不在当前视层）。

### 自定义角色颜色

导入 Blender 后直接改材质 Base Color 即可，无需在 Mixamo 网站切换角色。

## 与 Kimodo 对比

| | Mixamo | Kimodo |
|------|--------|--------|
| 动作来源 | 专业动捕 | AI 扩散模型 |
| 数量 | 2500+ | 无限（文字自由生成） |
| 质量 | 稳定可预测 | 可能有艺术伪影 |
| 中文搜索 | 仅英文 | 英文 prompt |
| 离线 | 需联网下载 | 本地 GPU 推理 |
| 安装 | 无需 | ~10GB 模型 |

**推荐策略**：常规动作先用 Mixamo（快且稳定），Mixamo 搜不到的精确用 Kimodo 生成。
