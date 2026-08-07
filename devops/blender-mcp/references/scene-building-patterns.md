# 场景搭建可复用模式

通过 `execute_blender_code` 搭建 3D 场景的标准化模板。

## 最小环境模板

```python
import bpy, math
from mathutils import Vector

# ====== 清空 ======
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
for m in list(bpy.data.materials): bpy.data.materials.remove(m)

# ====== 材质工厂（兼容中英文 Blender） ======
def mkmat(name, col, rough=0.7, metal=0, emit=0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    for n in m.node_tree.nodes:
        if n.type == 'BSDF_PRINCIPLED':  # 按类型找，不用中文名
            n.inputs["Base Color"].default_value = (*col, 1.0)
            n.inputs["Roughness"].default_value = rough
            n.inputs["Metallic"].default_value = metal
            n.inputs["Emission Strength"].default_value = emit
    return m

# ====== 快捷几何 ======
def bx(n, loc, scl, mt):
    bpy.ops.mesh.primitive_cube_add(location=loc, scale=scl)
    o=bpy.context.object; o.name=n
    if mt: o.data.materials.append(mt); return o
def cy(n, loc, r, d, rot, mt):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, location=loc, rotation=rot)
    o=bpy.context.object; o.name=n
    if mt: o.data.materials.append(mt); return o
def sp(n, loc, r, mt):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc)
    o=bpy.context.object; o.name=n
    if mt: o.data.materials.append(mt); return o
def tx(n, text, loc, size, ext, mt):
    bpy.ops.object.text_add(location=loc)
    o=bpy.context.object; o.name=n; o.data.body=text
    o.data.size=size; o.data.extrude=ext; o.data.align_x='CENTER'
    if mt: o.data.materials.append(mt); return o
```

## 可动小人模板

```python
hr, tw, lr = 0.12, 0.18, 0.06  # 头半径/躯干宽/四肢半径

# 蹲姿（人物靠柱）
HX, HY, HZ = -2.4, 1.8, 0.1
cy("h_cL",(HX,HY+0.13,HZ+0.08), lr,0.16, (0,0,0), MP)      # 左小腿
cy("h_cR",(HX,HY-0.13,HZ+0.08), lr,0.16, (0,0,0), MP)      # 右小腿
cy("h_tL",(HX+0.10,HY+0.13,HZ+0.18), lr,0.22, (math.pi/2,0,0), MP)  # 左大腿
cy("h_tR",(HX+0.10,HY-0.13,HZ+0.18), lr,0.22, (math.pi/2,0,0), MP)  # 右大腿
t = bx("h_torso",(HX+0.06,HY,HZ+0.28), (tw,0.14,0.31), MG)
t.rotation_euler = (0, math.radians(20), 0)               # 身体前倾
sp("h_head",(HX+0.04,HY,HZ+0.52), hr, MK)                 # 头
cy("h_aUL",(HX+0.06,HY+0.20,HZ+0.42), lr,0.18, (0,math.pi/2,0), MG)  # 左上臂
cy("h_aUR",(HX+0.06,HY-0.20,HZ+0.42), lr,0.18, (0,math.pi/2,0), MG)  # 右上臂
cy("h_aLL",(HX+0.20,HY+0.20,HZ+0.30), lr,0.15, (0,0.3,0), MG)        # 左前臂
cy("h_aLR",(HX+0.20,HY-0.20,HZ+0.30), lr,0.15, (0,0.3,0), MG)        # 右前臂
sp("h_hL",(HX+0.25,HY+0.22,HZ+0.22), 0.05, MK)           # 左手
sp("h_hR",(HX+0.25,HY-0.22,HZ+0.22), 0.05, MK)           # 右手
```

### 姿态速查

| 姿态 | 关键参数 |
|------|---------|
| 蹲姿 | 大腿 `(math.pi/2,0,0)` 水平前伸，身体 `(0,radians(20),0)` 前倾，手臂 `(0,math.pi/2,0)`+`(0,0.3,0)` |
| 站立 | 腿 `(0,0,0)` 垂直 0.70m，身体 z+0.80，手臂 `(-0.2,0,0.3)` |
| 行走 | 腿 `(0,0,±radians(10))` 微张 0.65m，手臂 `(-0.2,0,∓0.5)` 前后摆动 |

## 光照模板

```python
# 黄昏阳光
sun = bpy.data.lights.new("Sun", 'SUN')
sun.energy = 6; sun.angle = math.radians(6)
sun.color = (1.0, 0.40, 0.06)  # 暖橙
so = bpy.data.objects.new("Sun", sun)
bpy.context.collection.objects.link(so)
so.location = (-12, -18, 10)   # 左后方高位

# 世界背景（黄昏天色）
w = bpy.context.scene.world; w.use_nodes = True
for n in w.node_tree.nodes:
    if n.type == 'BACKGROUND':
        n.inputs["Color"].default_value = (1.0, 0.45, 0.10, 1.0)
        n.inputs["Strength"].default_value = 0.45
```

## 摄像机模板

```python
camD = bpy.data.cameras.new("Cam"); camD.lens = 28
camO = bpy.data.objects.new("Cam", camD)
bpy.context.collection.objects.link(camO)
camO.location = (5.5, 2.0, 2.0)
tgt = Vector((-2.0, -5.0, 2.0))
camO.rotation_euler = (tgt - camO.location).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = camO

# 视口设置
for a in bpy.context.screen.areas:
    if a.type == 'VIEW_3D':
        s = a.spaces.active
        s.shading.type = 'MATERIAL'          # 材质预览
        s.region_3d.view_perspective = 'CAMERA'  # 摄像机视角
        break
```

## 分文件保存模式

当用户要求对比多个方案时，每个方案保存独立 .blend：

```python
import os
proj = r"C:\Users\...\ProjectName"
os.makedirs(proj, exist_ok=True)

# 方案 A: 全景
# ... 搭建场景 A 的元素 ...
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(proj, "SceneA_Full.blend"))

# 清空重建方案 B
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
# ... 搭建场景 B ...
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(proj, "SceneB_Core.blend"))
```

## 多方案场景结构

```
Projects/<ProjectName>/
├── SceneA_Full.blend      # 方案 A: 电影级全景（最大元素量）
├── SceneB_Core.blend      # 方案 B: 核心建筑+氛围（精简）
└── SceneC_Storyboard.blend # 方案 C: 分镜多机位（3+ 摄像机）
```

方案命名约定：
- A: 全景/完整版（Full, Complete）
- B: 核心/精简版（Core, Minimal）
- C: 分镜/多视角（Storyboard, MultiCam）
