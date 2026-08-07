# Rigify 人体角色创建

在 Blender 中通过 Rigify 创建可动假人的完整流程。

## 概述

Rigify = Blender 内置角色绑定插件。提供人体 MetaRig（159骨骼骨架模板）→ 生成控制 Rig（706骨骼，含 IK/FK/手指/面部控制器）。

## 步骤

### 1. 启用 Rigify

```python
bpy.ops.preferences.addon_enable(module="rigify")
```

### 2. 创建 MetaRig

```python
import bpy
from rigify.metarigs import human

bpy.ops.object.armature_add(location=(0,0,0))
arm = bpy.context.object
arm.name = "MetaRig"

bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.armature.select_all(action='SELECT')
bpy.ops.armature.delete()
human.create(arm)  # 填充 159 骨骼
bpy.ops.object.mode_set(mode='OBJECT')
```

### 3. 生成控制 Rig

```python
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.pose.rigify_generate()
rig = bpy.context.object  # RIG-MetaRig, 706骨骼
```

### 4. 创建皮肤网格 + 自动蒙皮

```python
# ... 创建/导入 body mesh ...
body.select_set(True)
rig.select_set(True)
bpy.context.view_layer.objects.active = rig
bpy.ops.object.parent_set(type='ARMATURE_AUTO')
```

### 5. 隐藏 MetaRig

```python
bpy.data.objects["MetaRig"].hide_set(True)
```

## 控制器体系

生成的 `RIG-MetaRig` 有 220 个控制器骨骼（从 706 总骨骼中过滤 DEF-/ORG-/MCH- 前缀得出）：

| 类别 | 示例名称 |
|------|---------|
| 根/躯干 | `root`, `torso`, `chest`, `hips` |
| 脊柱 FK | `spine_fk`, `spine_fk.001`, `spine_fk.002` |
| 头颈 | `neck`, `head` |
| 手臂 FK | `upper_arm_fk.L/R`, `forearm_fk.L/R`, `hand_fk.L/R` |
| 手臂 IK | `hand_ik.L/R`, `upper_arm_ik.L/R`, `upper_arm_ik_target.L/R` |
| 腿 FK | `thigh_fk.L/R`, `shin_fk.L/R`, `foot_fk.L/R` |
| 腿 IK | `foot_ik.L/R`, `thigh_ik_target.L/R`, `foot_heel_ik.L/R` |
| 手指 | `f_index.01_master.L/R`, `thumb.01_master.L/R` 等 |
| 面部 | `brow.*`, `lid.*`, `lip.*`, `jaw.*`, `eye.*`, `nose.*` |

## 姿势控制

### FK vs IK

Rigify 同时提供 FK 和 IK 控制器。默认情况下它们在不同的骨骼层上。通过 `bpy.ops.pose.rigify_generate()` 后可以通过 Rigify UI 面板切换，或者直接操作对应的控制器：

- **IK 方式写姿势**：设置 `foot_ik.L` 的位置和旋转，膝盖会自动弯曲
- **FK 方式写姿势**：旋转 `thigh_fk.L` / `shin_fk.L` / `foot_fk.L`

### 代码写姿势

```python
import bpy
from mathutils import Vector, Euler

rig = bpy.data.objects["RIG-MetaRig"]
bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode='POSE')
pb = rig.pose.bones

# 蹲姿示例（用 IK）
pb['torso'].location = Vector((0, 0, -0.2))
pb['torso'].rotation_quaternion = Euler((0.3, 0, 0), 'XYZ').to_quaternion()
pb['foot_ik.L'].location = Vector((0, -0.05, -0.35))
pb['foot_ik.R'].location = Vector((0, -0.05, -0.35))
pb['spine_fk'].rotation_quaternion = Euler((0.25, 0, 0), 'XYZ').to_quaternion()
pb['head'].rotation_quaternion = Euler((0.3, 0, 0), 'XYZ').to_quaternion()

bpy.ops.object.mode_set(mode='OBJECT')
```

## 皮肤网格创建方法对比

| 方法 | 质量 | 难度 | 适用场景 |
|------|------|------|---------|
| 球+柱体组合 | ⭐ | 低 | 原型/占位 |
| 球+柱+Voxel Remesh | ⭐⭐ | 低 | 快速连续曲面 |
| 程序化管状截面 | ⭐⭐ | 中 | 有身体比例的曲面 |
| CC0 下载模型 | ⭐⭐⭐⭐ | 低 | 正式项目 |
| 手动雕刻 | ⭐⭐⭐⭐⭐ | 高 | 专业级 |

## 陷阱

1. **`human.create()` 参数是 armature object 而非 context**——`human.create(arm_obj)`，不是 `human.create(bpy.context)`。
2. **MetaRig 的 FK 旋转会被 IK 覆盖**——同时操作 FK 和 IK 时，IK 优先级更高。写姿势前确认使用 IK 还是 FK 模式。
3. **`bpy.ops.pose.rigify_generate()` 需要 meta-rig 被选中且为 active object**。
4. **骨骼层用 `arm.data.collections` 而非 `arm.data.layers`**——新版 Blender (5.x) 已改 API。
5. **WGT 控制器网格在独立 collection 中**——`hide_set(True)` 需要 collection 级别的操作，不能逐个 hide。
6. **bpy 程序化生成的网格外观有硬天花板**——不要反复迭代代码微调形状。需要好看外观时用下载模型或手动建模。
