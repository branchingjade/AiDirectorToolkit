# 飞书 docx「图文并茂」图源工作流

> 完整落地脚本，对应 SKILL.md「五·七、docs 嵌入图片」章节。所有参数基于 2026-09-03 伏妖记美术考据实战验证。

## 适用场景

- 创作类产出（剧本插图、美术考据、分镜示意、产品展示）要"图文并茂"落飞书
- 涉及实物参考（文物/艺术品/影视道具/历史图片）的证据链任务
- 用户说"贴参考图""附图""图文并茂""有理有据"到飞书 docs

## 端到端脚本

```python
"""
feishu_doc_image_embed.py — 飞书 docs 图源嵌入端到端工作流

用法：
  1. 编辑 IMAGE_SOURCES 列表（实物名 + 中文文件名）
  2. 准备好 lark-cli 已认证（hermes 默认 bot 身份）
  3. python feishu_doc_image_embed.py
"""

import os
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request

# ===== 配置 =====
DOC_TOKEN = '目标飞书 doc token'
TEXT_FILE = r'C:\Users\HMSJ\_content\<text>.md'  # 已写好的 markdown 内容（不含图片语法）

IMAGE_SOURCES = [
    # (中文显示名, Wikimedia 文件名, 压缩后输出名)
    ('越王勾践剑', '越王勾践剑.jpg', '越王勾践剑.jpg'),
    ('清明上河图', '清明上河图.jpg', '清明上河图_small.jpg'),  # 大图压缩
    # ...
]

CWD_IMG_DIR = r'C:\Users\HMSJ\Documents\Hermes\_imgs'  # lark-cli 唯一接受的相对路径
FFMPEG = r'C:/Users/HMSJ/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.1.1-full_build/bin/ffmpeg.exe'
LARK = r'C:\Users\HMSJ\AppData\Local\hermes\node\lark-cli.CMD'

# ===== 1. Wikimedia 探测 + 下载 =====
def fetch_wikimedia(name, dst_filename):
    """Special:FilePath 探测 → 302 真实 URL → urllib 拉本地"""
    src_url = f'https://commons.wikimedia.org/wiki/Special:FilePath/{urllib.parse.quote(name)}'
    dst_path = os.path.join(CWD_IMG_DIR, dst_filename)

    # HEAD 探测 + 302
    try:
        req = urllib.request.Request(src_url, method='HEAD', headers={'User-Agent': 'Mozilla/5.0 (research)'})
        with urllib.request.urlopen(req, timeout=15) as r:
            real_url = r.url.split('?')[0]  # 去掉 utm 参数
            if r.status != 200:
                print(f'[{name}] HEAD fail: {r.status}')
                return False
    except Exception as e:
        print(f'[{name}] HEAD error: {e}')
        return False

    # 退避 + GET
    for attempt in range(3):
        try:
            time.sleep(2 + attempt * 5)  # 2/7/12 秒退避，防 429
            req = urllib.request.Request(real_url, headers={'User-Agent': 'Mozilla/5.0 (research)'})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
            with open(dst_path, 'wb') as f:
                f.write(data)
            size_kb = len(data) // 1024
            print(f'[{name}] OK {size_kb} KB')
            return True
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 2:
                print(f'[{name}] 429, retry after {5*(attempt+1)}s')
                continue
            print(f'[{name}] FAIL: {e}')
            return False
        except Exception as e:
            print(f'[{name}] FAIL: {e}')
            return False
    return False


# ===== 2. ffmpeg 大图压缩 =====
def compress_if_large(filepath, max_kb=3000):
    """>max_kb 的图缩到 2400px 宽 + q:v=5"""
    size_kb = os.path.getsize(filepath) // 1024
    if size_kb <= max_kb:
        return filepath

    dst = filepath.replace('.jpg', '_small.jpg')
    cmd = [FFMPEG, '-y', '-i', filepath, '-vf', 'scale=2400:-2', '-q:v', '5', dst]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        print(f'  compress fail: {r.stderr[-200:]}')
        return filepath  # 失败回退原图
    print(f'  compressed: {size_kb} KB → {os.path.getsize(dst) // 1024} KB')
    return dst


# ===== 3. 写文本（不含 markdown 图片语法） =====
def write_text(doc_token, text_file):
    """docs +update --command overwrite"""
    # 先把 text_file 复制到 cwd 下（lark-cli --content 必须是 cwd 相对）
    cwd_text = os.path.join(os.getcwd(), '_text.md')
    shutil.copy(text_file, cwd_text)

    cmd = [LARK, 'docs', '+update',
           '--doc', doc_token,
           '--doc-format', 'markdown',
           '--command', 'overwrite',
           '--content', '@_text.md']
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60, shell=True)
    if r.returncode != 0:
        print(f'write_text FAIL: {r.stderr[:300]}')
        return False
    print(f'write_text OK: {r.stdout[:200]}')
    return True


# ===== 4. media-insert 逐张插图 =====
def insert_image(doc_token, img_relpath, caption, width=1200):
    cmd = [LARK, 'docs', '+media-insert',
           '--doc', doc_token,
           '--file', img_relpath,
           '--caption', caption,
           '--width', str(width)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120, shell=True)
    if r.returncode != 0:
        print(f'  insert FAIL: {r.stderr[:300]}')
        return False
    print(f'  insert OK: {os.path.basename(img_relpath)}')
    return True


# ===== 5. 验证 =====
def verify_images(doc_token):
    cmd = [LARK, 'docs', '+fetch',
           '--doc', doc_token,
           '--scope', 'full',
           '--detail', 'full',
           '--format', 'pretty']
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30, shell=True)
    import re
    names = re.findall(r'<img [^>]*name="([^"]+)"', r.stdout)
    return names


# ===== Main =====
def main():
    # 准备 cwd img dir
    if os.path.exists(CWD_IMG_DIR):
        shutil.rmtree(CWD_IMG_DIR)
    os.makedirs(CWD_IMG_DIR, exist_ok=True)

    # 1. 下载全部图
    print('=== STEP 1: Wikimedia 下载 ===')
    downloaded = []
    for display, fname, out_name in IMAGE_SOURCES:
        if fetch_wikimedia(fname, out_name):
            downloaded.append((display, out_name))

    # 2. 大图压缩
    print('\n=== STEP 2: ffmpeg 压缩 ===')
    for display, out_name in downloaded:
        fp = os.path.join(CWD_IMG_DIR, out_name)
        compressed = compress_if_large(fp)
        if compressed != fp:
            # 把压缩后文件名同步到 IMAGE_SOURCES
            for i, (d, fn, on) in enumerate(IMAGE_SOURCES):
                if d == display:
                    IMAGE_SOURCES[i] = (d, fn, os.path.basename(compressed))
                    break

    # 3. 写文本
    print('\n=== STEP 3: 写文本 ===')
    if not write_text(DOC_TOKEN, TEXT_FILE):
        sys.exit(1)

    # 4. 插图
    print('\n=== STEP 4: media-insert ===')
    for display, fname, out_name in IMAGE_SOURCES:
        rel_path = f'./_imgs/{out_name}'
        if not insert_image(DOC_TOKEN, rel_path, display):
            print(f'  {display} 跳过')
        time.sleep(1)  # 防限流

    # 5. 验证
    print('\n=== STEP 5: 验证 ===')
    embedded = verify_images(DOC_TOKEN)
    print(f'文档中嵌入的图片: {embedded}')
    expected = [on for _, _, on in IMAGE_SOURCES]
    missing = set(expected) - set(embedded)
    if missing:
        print(f'⚠️ 缺失: {missing}')
        sys.exit(1)
    print('✅ 全部图嵌入成功')


if __name__ == '__main__':
    main()
```

## 必读陷阱（与 SKILL.md 五·七 章节互补）

### 触发场景

- 用户明确要求"图文并茂"到飞书 docs
- 涉及文物/实物参考的证据链任务
- 接到任何"写飞书文档 + 要图"的创作类任务

### 不要做的事

1. **不要在 markdown 文本里写 `![](URL)`** —— 飞书服务端 99% 拉不下来 Wikimedia/外网图
2. **不要传绝对路径给 `--file`** —— lark-cli 必报 `unsafe file path`
3. **不要先 media-insert 后 overwrite** —— overwrite 会把已嵌入的图冲掉
4. **不要高频 hit Wikimedia** —— 加 `time.sleep(2+attempt*5)` 退避，429 是常态
5. **不要传 >5MB 的图** —— 飞书 doc 翻页会卡，预先 ffmpeg 压缩

### 强制顺序（违反会导致图丢失）

```
写文本 → 验证 → 逐张 media-insert → 验证
       ↑                                   ↓
       不用 overwrite ← ← ← ← ← ← ← ← ← ←
```

### Wikimedia 中文文件名编码

中文文件名（"越王勾践剑.jpg"）直接拼 URL 会 404——必须 `urllib.parse.quote("越王勾践剑.jpg")`。`Special:FilePath/` 是 Wikimedia 的中转服务，会把 `File:<编码后>` 302 到真实 upload URL。

### ddgs / web_extract 后端选择（中文文物名检索）

中文文物名检索优先用 Wikimedia API + Chinese Wikipedia 反链——`ddgs` 对中文检索成功率低、Exa 仅英文。

```python
# 找 Wikimedia 文件名的反链
import urllib.request, urllib.parse, json
api = 'https://zh.wikipedia.org/w/api.php?action=query&titles=<人物/器物>&prop=images&format=json'
data = json.loads(urllib.request.urlopen(api, timeout=15).read())
for page in data['query']['pages'].values():
    for img in page.get('images', []):
        print(img['title'].replace('File:', ''))
```

## 配套 SKILL.md 章节

- `SKILL.md` 第五·七节 = 「docs 嵌入图片到 docx」（坑矩阵）
- `SKILL.md` 第五·六节 = 「docs +update 文本替换」（str_replace 模式）

## 不适用

- **中文站反爬内容**（百度/知乎/豆瓣）→ 走 `browser-control` 或 Kimi WebBridge，不是本工作流
- **用户真实浏览器登录态** → 走 Kimi WebBridge session
- **结构化 JSON 数据** → 走 `web-content-extractor`，不是图源工作流

## 实战失败案例（2026-09-03 伏妖记美术考据）

把这次的实物图源抓取失误记下来——给未来同类任务避坑。

### 失败 1：Commons "Garuda_cliff_in_Tirumala" 文件名误导

**任务**：伏妖记素鸢金翅鸟本体的视觉参考

**抓的图**：`Special:FilePath/Garuda_cliff_in_Tirumala.jpg` HEAD 200，3.6MB 看着像巨岩

**为什么错**：commons 上**没有真正的敦煌金翅鸟图**——这个文件是 Tirumala（印度教圣地）的天然山崖"鸟形轮廓"，**不是金翅鸟造像/雕塑/壁画**。`vision_analyze` 出来才发现是自然山岩。

**修法**：
- 下载后立刻 `vision_analyze` 验证「这是金翅鸟/迦楼罗吗」——答 yes 才用
- 答 no 直接 `docs +update --command block_delete --block-id <img_id>` 删除，留档「需要用浏览器去敦煌研究院官网/台北故宫找真品图」
- 飞书 doc 的 image block_id 从 fetch 的 `<img ... id="...">` 提取

**避坑前置**：抓之前先 `web_search` 搜"敦煌 金翅鸟 迦楼罗 壁画 图"看中文圈是否已有；去 commons Category:Garuda (mythology) 看分类；WikiCommons 中文分类「金翅鸟」「迦楼罗」通常没图。

### 失败 2："江帆楼阁图" 不是台北故宫真迹

**任务**：唐代金碧山水的最高范式视觉参考

**抓的图**：`Special:FilePath/江帆樓閣圖.jpg` HEAD 200，329KB 看着是金碧山水

**为什么错**：WikiCommons 上**没有李思训台北故宫真迹**（国宝级文物不允许外网下载）。下到的图虽然是金碧/青绿山水范式作品（赭红暖背景+石绿山石+楼阁一角），但**不一定是李思训原迹**——可能是仿本/后摹/明代画家临本。`vision_analyze` 出来是金碧范式但无法确认作者。

**修法**：
- caption 加诚实标注：**"WikiCommons 来源仿/摹本，原作出自李思训风格，台北故宫博物院藏原迹；本图作金碧山水范式参考"**
- 不删除——图本身范式有用，**图范式 + caption 标注真实出处**是更负责任的处理
- 真品图需要浏览器去台北故宫官网（不让外网下载）+ 故宫博物院数字文物库（有公开高清扫描）
- 同样范式：敦煌壁画真品 → 敦煌研究院官网；故宫文物真品 → 故宫数字文物库（digicol.dpm.org.cn）

### 失败 3：先 media-insert 后 overwrite 文本——图被冲掉

**任务**：写完文本 + 嵌入 5 张文物图 + 调整文本

**错误顺序**：
```
1. media-insert 5 张图（成功，5 个 img block）
2. overwrite 全文文本（把图片块当成内容覆盖）
```

**为什么错**：`docs +update --command overwrite --content @file.md` 是"全文覆盖"——**已有的 image block 不在 @file.md 文本里**，被当成"要被覆盖的内容"冲掉。冲掉的图实际**没消失**，被推到了文末（但 caption 与文本上下文错位）。

**正确顺序**（已在 SKILL.md 坑 4 说明）：
```
1. overwrite 全文文本（不含 markdown 图片语法）
2. media-insert 5 张图
3. 后续调整文本：只能用 str_replace / block_replace / block_insert_after——不要再 overwrite
```

**如果已经踩坑**：用 `block_delete --block-id <img_id>` 删错位图（注意：从 fetch XML 的 `<img id="..." name="...">` 提取 id），重新 `media-insert` 让图回到正位。

### 失败 4：block_replace 改 image caption 把图替换成 caption 文本

**任务**：已经嵌入飞书的图 caption 不准确（"江帆楼阁图（传唐·李思训，台北故宫博物院藏）" → 需要改成"WikiCommons 来源仿/摹本..."），想只改 caption 不动图

**错误操作**：
```
docs +update --command block_replace --block-id <img_id> --content "新 caption 文本"
```

**为什么错**：`block_replace` 是「用一个 block 替换另一个 block」——`--content` 是新 block 的完整 XML 字符串。传纯 caption 文本 = 创建一个 paragraph block 替换 image block = **图没了，只剩 caption 文本**。

**正确改 caption 的两种方法**：
- **方法 A**：传完整 `<img>` 标签（带新 caption）：
  ```
  docs +update --command block_replace --block-id <img_id> --content '<img src="<file_token>" caption="新 caption" width="1200"/>'
  ```
  但 file_token 需要从 fetch XML 拿，不便
- **方法 B**（更稳妥）：**删旧图 + media-insert 新图**：
  ```
  docs +update --command block_delete --block-id <old_img_id>
  docs +media-insert --doc <token> --file ./_imgs/foo.jpg --caption "新 caption"
  ```

**避坑**：永远不要对 image block 单独改 caption——要么传完整 `<img>` XML，要么删旧插新。

## 相关引用

- `SKILL.md` 五·六节 — docs +update str_replace 文本替换坑（block_replace 后 ID 失效等）
- `SKILL.md` 五·七节 — 图嵌入坑矩阵（4 个核心坑 + 完整工作流）
- `references/feishu-obsidian-sync.md` — 飞书↔Obsidian 文档角色三分法