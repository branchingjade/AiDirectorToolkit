---
name: feishu-image-analysis
description: "分析飞书群里的图片时用：lark-cli 取图链路+气质评审四维。触发词：分析上面的图片、阴不阴、这张图怎么样。"
version: 1.0.0
author: Hermes
license: MIT
tags: [feishu, lark-cli, image-analysis, character-design, review]
metadata:
  hermes:
    tags: [feishu, lark-cli, image-analysis, character-design, review]
    related_skills: [妖玉影视知识库, lark-im]
---

# 飞书群图分析（取图 + 评审）

> 飞书群里有人发图、有人引用它说「分析上面的图片」——图片不会自动落到本地，取图要走 lark-cli；评审要走导演尺子。两个半段都在这。

## When to Use

- 飞书会话里用户引用一张图说「分析上面的图片」「这张图怎么样」「阴不阴」「看看这个角色设计」
- 常见于创作协作群：成员发 AI 生成的角色设计图/分镜参考图，导演/制片让 bot 评审
- 图片在群里但 bot 拿不到文件时（飞书图片不落本地磁盘）
- **影视项目群**：评审前按 妖玉影视知识库 主动工作协议加载（导演底色/美学尺子/制作严谨三视角，skill_view(name='妖玉影视知识库')），评审输出用导演语言

## 核心事实（先记住，别白找）

1. 飞书图片消息**不会**落到本地磁盘——用户消息正文里只有占位（`[Image]` / `![Image](img_v3_xxx)`）。本地 media/uploads 目录为空是常态，别去瞎 find。
2. 被引用图片的 file_key 在**原消息**的 content 里（`![Image](img_v3_0214i_...)\n文字`），不在引用它的那条消息里——引用消息正文只有 `[Replying to: "..."]`。
3. 取图链路 = 找群 chat_id → 列群消息找含图原消息 → 抠 file_key → lark-cli 下载 → vision_analyze。

## 取图链路（实测可用，2026-08-14）

1. **找群**（按群名辨认）：
   ```
   lark-cli im +chat-list
   ```
   输出 `data.chats[]`：`chat_id`（oc_xxx）、`name`。

2. **列群消息，找含图原消息**：
   ```
   lark-cli im +chat-messages-list --chat-id oc_xxx --page-size 20
   ```
   - 图片消息 msg_type 通常是 `post`，content 形如 `![Image](img_v3_0214i_...)\n阴不阴`，带 `message_id`（om_xxx）
   - 线程回复在 `thread_replies[]` 里，同样含完整 content 与 message_id
   - 消息太多时按 create_time 定位；引用消息与被引用消息在同一条目内相邻出现

3. **下载**（先 cd 到用户目录下的目标文件夹，--output 只收相对路径）：
   ```
   cd ~/Documents/Hermes/tmp_img
   lark-cli im +messages-resources-download --message-id om_xxx --file-key img_v3_xxx --type image --output <文件名>
   ```
   落盘文件自动带扩展名（如 `fuyou_img.jpg`，从 Content-Type 推断）。

4. **分析**：`vision_analyze` 传 Windows 绝对路径（如 `C:\Users\HMSJ\Documents\Hermes\tmp_img\fuyou_img.jpg`）；无视觉模型时自动走辅助视觉模型。

## 坑（实测）

- `--type image` 必填——缺了报 `required flag(s) "type" not set`（validation error）
- `--output` **只接受相对路径**（禁 `..` 遍历）——先 cd 到目标目录再传裸文件名
- file_key 从消息 content 的 `![Image](...)` 里抠，格式 `img_v3_xxx`，别手输
- 图片消息的 `content` 是富文本 post 格式，不是 `{"image_key": ...}` JSON——直接正则抠 `img_v3_[A-Za-z0-9_]+`
- 下载成功后立刻 vision_analyze，别用 read_file 读二进制（read_file 不支持图片）

## 评审框架：角色设计图气质判定（四维）

用户问「阴不阴/好不好/怎么样」时，按四维拆开给依据，不拍脑袋下结论：

| 维度 | 「贵/仙/冷」的读法 | 「阴」的读法 |
|---|---|---|
| **光** | 正面柔光，面部全亮、轮廓清晰（打光打得很客气） | 顶光/侧逆光，面部大半沉进暗部，留一只眼睛在光里（半边脸拍法） |
| **色** | 冷色+暖光斑的冷暖对比，落点=华贵 | 冷绿/幽蓝/暗紫，环境整体压暗，暖色全灭 |
| **姿态** | 端坐/正对镜头/上位者宣示 | 微侧、垂眼、藏手、坐姿松垮或俯视 |
| **眼神** | 清冷疏离（淡） | 有「算」——半眯、眼白多、视线压人（毒） |

**关键原则：**
- **贵气不是阴气**——方向不同的气质，元素堆再多也到不了（「贵气堆满了，但贵气不是阴气」）。方向错了先换方向（光位/眼神两刀最快），再谈细节
- **定位先行**：先确认角色定位再给改法——定位本就是「贵而清冷」（如镜妖式反差角色），现版就对了，别为「阴」去动它；定位是「阴」才按四维调。评审收尾给一个定位确认问题（「这角色是哪一位？需要按定位给具体方向」）
- **制作落地**：AI 生成图当角色锚点/分镜参考可用，但气质要能在实拍/CG 里复现——无形无锚点的设计是废设计
- 改法按性价比排序给 2-3 条（光 > 眼神 > 环境色），不堆 10 条

## 输出规范（群聊场景）

- 结构：一句话定性（「不阴，是冷贵」）→ 四维依据 → 排序改法 → 定位确认问题
- 用导演语言（光/色/构图/气质），不用术语堆砌；国风项目禁三幕/弧光等结构术语（视觉分析语言不受此限）
- 群聊回复长度适中，不写论文
