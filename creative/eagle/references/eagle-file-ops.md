# Eagle 文件操作：路径发现 + 覆写

## 场景

Eagle 中已有 `男.fbx` / `女.fbx`（带 Mixamo 动画），需要清除动画、应用 Mixamo Rig IK 控制后覆盖原文件。

## 步骤

### 1. 通过缩略图 API 找到文件路径

```python
def get_item_dir(item_id):
    """从 Eagle thumbnail API 反推文件所在目录"""
    r = api('GET', f'/item/thumbnail?id={item_id}')
    thumb = r['data']  # "Y:/HMSJ_B.library/images/MR36XXX.info/男_thumbnail.png"
    return thumb.rsplit('_thumbnail.png', 1)[0]

# 例：男.fbx → Y:/HMSJ_B.library/images/MR360EKT3JXBG.info/
```

库路径模式：
```
<盘符>:/<库名>.library/images/<ITEM_ID>.info/<文件名>.<ext>
```

用户库位置：`Y:/HMSJ_B.library/`

### 2. Blender 处理：导入 → 清动画 → Mixamo Rig → 导出

```python
import bpy

# === 清场景 ===
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
for m in list(bpy.data.meshes): bpy.data.meshes.remove(m)
for a in list(bpy.data.armatures): bpy.data.armatures.remove(a)
for mat in list(bpy.data.materials): bpy.data.materials.remove(mat)
for act in list(bpy.data.actions): bpy.data.actions.remove(act)

# === 导入 ===
bpy.ops.import_scene.fbx(filepath="Y:/..../男.fbx")

# === 清除动画 ===
for action in list(bpy.data.actions):
    bpy.data.actions.remove(action)

# === Mixamo Rig IK ===
# ⚠️ 必须选中骨架（ARMATURE），不是身体网格（MESH）
arm = None
for obj in bpy.data.objects:
    if obj.type == 'ARMATURE':
        arm = obj
        break

bpy.ops.object.select_all(action='DESELECT')
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.mr.make_rig()

# === 导出（仅必要对象，排除 cs_ 控制形状） ===
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.data.objects:
    if obj.type in ('MESH', 'ARMATURE') and not obj.name.startswith('cs_'):
        obj.select_set(True)

bpy.ops.export_scene.fbx(
    filepath=out_path,
    use_selection=True,           # ← 核心：只导出选中的
    add_leaf_bones=False,
    bake_anim=False
)
```

导出后应为 3 个对象：身体 MESH + 关节 MESH + 骨架 ARMATURE，168 骨骼（65 原始 mixamorig + 103 IK/控制），无动画。

### 3. 直接覆写 Eagle 库文件

```bash
cp "新文件" "Y:/HMSJ_B.library/images/<ITEM_ID>.info/原文件名"
```

Eagle 不会重新索引——元数据不变，只有文件内容被替换。

### 4. 验证

用 `item/list?folders=<ID>` 确认文件仍在文件夹中。

## 陷阱

- **Eagle 的「使用已存在文件导入」不会覆盖文件**，只是跳过导入。必须用磁盘覆写（`cp`）。
- **API 不支持更新文件内容**，只能覆写磁盘。
- **`mr.make_rig()` 必须选中骨架**：选中 MESH 身体 → `poll() failed`；选中 ARMATURE → 成功。
- **导出必须用 `use_selection=True`**：否则会带上 Mixamo Rig 生成的 20+ 个 `cs_` 控制形状物体。
- **不要反复导出覆盖同一文件**：每次导出前确认当前场景是干净导入的状态，避免把前次导出残留的控制形状再次打包。
- **验证用 `item/list?folders=<ID>`**，不要依赖 `folder/list` 的树（有缓存延迟）。
- **`bpy.ops.object.select_all()` 在某些 Blender 上下文会报 `poll() failed`**，用 `bpy.data.objects.remove()` 替代。
- **原始文件备份**：在覆盖 Eagle 文件前，先 `cp` 备份到本地 Projects 目录。一旦导出出错（如 4KB 空文件），可快速还原。
