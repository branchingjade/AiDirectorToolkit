# Kimodo Blender Bridge

## 概述

Kimodo 是 NVIDIA 的运动扩散模型（700 小时动捕训练）。Blender Bridge 通过子进程桥接：Blender addon ↔ Kimodo venv ↔ GPU 推理。

## 安装

1. 下载 zip → Blender Add-ons → Install from Disk → 启用 "Kimodo Motion Generator"
2. N 键 → Kimodo → Connection → **Install Kimodo (Auto)**
   - 创建 `~/.kimodo-venv/`
   - 安装 PyTorch CUDA 12.1 + Kimodo (Aero-Ex fork)
   - 下载 LLM2Vec 文本编码器
   - 下载 Kimodo-SOMA-RP-v1 模型权重
   - 约需 10GB 磁盘，5-15 分钟

## 启动

Connection 面板 → **Start Kimodo**（首次 10-60 秒加载模型）

## 模型

默认使用 **Kimodo-SOMA-RP-v1**（SOMA 77 关节骨架，700h Rigplay 数据）。其他可选：G1（机器人骨架）、SMPL-X。

## 帧率

**Kimodo 固定 30 FPS**。场景建议统一 30 FPS。如果场景不同帧率，Bridge 会自动做帧率映射。

## 生成动作

Motion Segments 面板：
1. Add → 输入 **英文 prompt**（LLM2Vec 文本编码器仅支持英文，中文 prompt 会产生乱码动作）
2. **Generate Selected**（单段）或 **Generate All**（多段连续）
3. Kimodo_Source 骨架出现，带动画

**典型可用 prompt**：
- `a worker crouches against a concrete pillar, resting` — 蹲靠柱子
- `a person walks slowly through an industrial corridor` — 慢走过道
- `someone sits on the ground leaning against a wall, tired` — 坐靠墙

约束类型：Root XZ（地面路径）、Full-Body（关键帧姿态）、Hand/Foot（末端效应器）

## 重定向到角色

Retarget 面板：
1. Source = Kimodo_Source，Target = 你的角色骨架
2. Auto-Match Bones（模糊匹配骨骼名）
3. Apply Constraints
4. Bake & Remove Constraints（烘焙关键帧并清理）

## 陷阱

1. **Quick Generate vs Segments**：直接用 `s.prompt = "..."` + `bpy.ops.kimodo.generate()` 可能无声失败。推荐用 Motion Segments UI。
2. **VRAM**：默认 ~17GB。开 `TEXT_ENCODER_DEVICE=cpu` 降到 <3GB。
3. **Web Demo 独立进程**：`kimodo_demo` 命令启动 Gradio 界面（localhost:7860），与 Bridge 互斥——同一时间只能一个进程加载模型。Blender Bridge 启动后不自动启动 Web Demo。
4. **30fps 硬限制**：模型训练数据即 30fps，无法生成其他帧率。Bridge 会换算但建议场景统一。
5. **bpy API 属性**：生成参数在 `bpy.context.scene.kimodo` 上：
   - `s.prompt` — 动作文字描述（英文）
   - `s.duration` — 时长（秒）
   - `s.seed` — 随机种子
   - `s.kimodo_model` — 模型名称（默认 Kimodo-SOMA-RP-v1）
   - `s.is_connected` — 桥接状态（bool）
   - `s.is_generating` — 是否生成中
   - `s.connection_status` — 状态文本（如 "Ready — Kimodo-SOMA-RP-v1 on cuda:0 (30 fps)"）
   - `s.motion_segments` — 分段列表集合
6. **生成后验证**：成功后 `Kimodo_Source` 骨架出现（78骨头），含动画（`obj.animation_data.action.frame_range`）。
7. **重定向**：Retarget 面板 → Auto-Match Bones → 模糊匹配 Kimodo SOMA 骨骼名到目标 Rigify/MB-Lab 骨架 → Apply Constraints → Bake。
