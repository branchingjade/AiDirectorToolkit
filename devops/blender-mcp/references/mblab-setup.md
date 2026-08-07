# MB-Lab 安装与用法

## 安装

```python
# 从 GitHub master 下载
url = "https://github.com/animate1978/MB-Lab/archive/refs/heads/master.zip"
# 解压到 %APPDATA%/Blender Foundation/Blender/5.1/scripts/addons/MB-Lab-master/
# 启用模块 "MB-Lab-master"
```

## Blender 5.1 兼容性修复

MB-Lab 的 `humanoid.py` 在 `get_subd_visibility()` 和 `update_character()` 中缺少 None 检查，当角色对象不存在时会崩溃。

### 修复 1：`get_subd_visibility` + `set_subd_visibility`

```python
# humanoid.py line ~545
def get_subd_visibility(self):
    obj = self.get_object()
    if obj is None:          # ← 添加
        return False         # ← 添加
    modfr = algorithms.get_modifier(obj, self.mat_engine.subdivision_modifier_name)
    return algorithms.get_modifier_viewport(modfr)

def set_subd_visibility(self, value):
    obj = self.get_object()
    if obj is None:          # ← 添加
        return               # ← 添加
    modfr = algorithms.get_modifier(obj, self.mat_engine.subdivision_modifier_name)
    algorithms.set_modifier_viewport(modfr, value)
```

### 修复 2：`update_character`

```python
# humanoid.py line ~756
def update_character(self, category_name=None, mode="update_all"):
    time1 = time.time()
    obj = self.get_object()
    if obj is None:                          # ← 添加
        logger.warning("...")                # ← 添加
        return                               # ← 添加
    self.clean_verts_to_process()
```

## 程序化角色创建（全自动）

### 关键：必须先设类型，且清空所有残留数据

```python
import bpy

# 彻底清空（不仅是场景删除！）
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
for mesh in list(bpy.data.meshes): bpy.data.meshes.remove(mesh)
for mat in list(bpy.data.materials): bpy.data.materials.remove(mat)
for arm in list(bpy.data.armatures): bpy.data.armatures.remove(arm)

# ⭐ 必须在 init_character 之前设置！
bpy.context.scene.mblab_character_name = 'm_as01'  # 亚洲男性
# 或 'f_as01'（女性）、'm_ca01'（白人男性）等

bpy.ops.mbast.init_character()

# 验证
for obj in bpy.data.objects:
    if obj.type == 'MESH' and len(obj.data.vertices) > 10000:
        print(f"{obj.name} ({len(obj.data.vertices)}v)")
        break
```

### 可用角色类型

| ID | 描述 |
|----|------|
| `m_af01` | 非洲男性 |
| `m_as01` | 亚洲男性 |
| `m_ca01` | 白人男性 |
| `m_la01` | 拉丁男性 |
| `f_af01` | 非洲女性 |
| `f_as01` | 亚洲女性 |
| `f_ca01` | 白人女性 |
| `f_la01` | 拉丁女性 |
| `m_an01`-`03` | 动漫男性 |
| `f_an01`-`03` | 动漫女性 |
| `m_ft01`-`02` | 奇幻男性（精灵/矮人） |
| `f_ft01` | 奇幻女性（精灵） |

## 白模转换

MB-Lab 使用纹理节点覆盖 Base Color。转白模需**删除所有 TEX_IMAGE 节点 + 断开 BSDF 输入连线**：

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

只改 Base Color 不够——纹理节点仍连接在 BSDF 上覆盖了颜色。

## 陷阱

1. **数据残留导致性别复用**：`bpy.ops.object.delete()` 只清场景，`bpy.data.objects` 中残留的旧骨架/mesh 会导致新角色沿用旧类型。必须 `bpy.data.objects.remove()` 全部清理。
2. **`character_generator` 崩溃**：该操作符在角色对象不存在时调用 `get_subd_visibility()` 导致 `AttributeError: 'NoneType' object has no attribute 'modifiers'`。应用上述修复 1+2。
3. **ENUM 属性设置**：`mblab_character_name` 是动态 EnumProperty，直接赋值 `= 'm_as01'` 有效但不会触发 update 回调。仅在 init_character 前设置即可，回调只用于更新 UI 选项列表。
