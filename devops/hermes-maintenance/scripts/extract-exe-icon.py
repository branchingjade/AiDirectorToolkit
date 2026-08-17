#!/usr/bin/env python3
"""提取 Windows exe 内嵌 PNG 图标并对比官方 ICO 资源 — 诊断「Hermes 图标怎么变了」类问题。

背景: Hermes 桌面 app 是本地构建 (apps/desktop/release/win-unpacked/Hermes.exe),
`hermes update` 不重建桌面 app。exe 壳图标(PE 资源段内嵌 PNG)可能与 app.asar 内
assets/icon.ico(资源文件)不一致 — 用户看到"原子/轨道图标"= electron-builder 构建时
回退到 Electron 默认图标; 官方图标从未变过(二次元少女, 7 帧 ICO)。

用法:
  python extract-exe-icon.py <Hermes.exe路径> [输出目录]
  python extract-exe-icon.py --ico <icon.ico路径>   # 只看官方 ico 帧结构
"""
import os
import re
import struct
import sys


def extract_exe_icons(exe_path: str, outdir: str) -> list:
    """扫描 exe 内所有 PNG 签名, 提取 256x256 的(即壳图标), 返回 [(idx,w,h,path)]."""
    os.makedirs(outdir, exist_ok=True)
    data = open(exe_path, "rb").read()
    pngs = [m.start() for m in re.finditer(rb"\x89PNG\r\n\x1a\n", data)]
    found = []
    for i, p in enumerate(pngs):
        try:
            w, h = struct.unpack(">II", data[p + 16 : p + 24])
        except struct.error:
            continue
        if w == 256 and h == 256:
            end = data.find(b"IEND", p)
            if end == -1:
                continue
            chunk = data[p : end + 8]
            fn = os.path.join(outdir, f"exe_icon_{i}_{w}x{h}.png")
            with open(fn, "wb") as f:
                f.write(chunk)
            found.append((i, w, h, fn))
    return found


def ico_frames(ico_path: str) -> list:
    """解析 ICO 目录表, 返回 [(w,h,bytes), ...]. 官方 Hermes ico 为 7 帧."""
    data = open(ico_path, "rb").read()
    _, _, count = struct.unpack("<HHH", data[:6])
    frames = []
    for i in range(count):
        off = 6 + i * 16
        w, h = data[off], data[off + 1]
        size = struct.unpack("<I", data[off + 8 : off + 12])[0]
        frames.append((256 if w == 0 else w, 256 if h == 0 else h, size))
    return frames


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "--ico":
        print("ICO frames:", ico_frames(sys.argv[2]))
    elif len(sys.argv) >= 2:
        exe = sys.argv[1]
        out = sys.argv[2] if len(sys.argv) >= 3 else "exe_icons"
        results = extract_exe_icons(exe, out)
        if not results:
            print("未找到 256x256 内嵌 PNG 图标")
        else:
            for idx, w, h, fn in results:
                print(f"提取 {w}x{h}: {fn}")
    else:
        print(__doc__)
