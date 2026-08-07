#!/usr/bin/env python3
"""
Extract and aggregate video technical metadata from davinci-resolve-mcp
analysis reports. Run after media_analysis analyze_sequence with depth=quick.

Usage:
    python scripts/extract-technical-report.py <analysis_root>

Output: aggregated codec, resolution, color space, bit depth, framerate stats.
"""

import json, os, sys
from collections import Counter

def main(analysis_root):
    clips_dir = os.path.join(analysis_root, 'clips')
    if not os.path.isdir(clips_dir):
        print(f"ERROR: clips directory not found: {clips_dir}")
        sys.exit(1)

    codecs = Counter()
    resolutions = Counter()
    color_spaces = Counter()
    color_transfers = Counter()
    pix_fmts = Counter()
    depths = Counter()
    framerates = Counter()
    outliers = []

    for dirname in sorted(os.listdir(clips_dir)):
        tech_path = os.path.join(clips_dir, dirname, 'technical.json')
        if not os.path.exists(tech_path):
            continue
        with open(tech_path) as f:
            tech = json.load(f)

        clip_name = dirname.rsplit('-', 1)[0]
        streams = tech.get('raw', {}).get('streams', [])

        for s in streams:
            if s.get('codec_type') != 'video':
                continue
            w, h = s.get('width', 0), s.get('height', 0)
            codec = s.get('codec_name', '?')
            cs = s.get('color_space', '?')
            ct = s.get('color_transfer', '?')
            pf = s.get('pix_fmt', '?')
            depth = s.get('bits_per_raw_sample', '?')
            rfr = s.get('r_frame_rate', '')

            codecs[codec] += 1
            resolutions[f'{w}x{h}'] += 1
            color_spaces[cs] += 1
            color_transfers[ct] += 1
            pix_fmts[pf] += 1
            depths[f'{depth}bit'] += 1

            if rfr and '/' in rfr:
                n, d = rfr.split('/')
                framerates[round(int(n)/int(d))] += 1

            if w != 3840 or h != 2160:
                fmt = tech.get('raw', {}).get('format', {})
                outliers.append({
                    'name': clip_name,
                    'res': f'{w}x{h}',
                    'codec': codec,
                    'color_space': cs,
                    'path': fmt.get('filename', 'N/A'),
                })

    total = sum(codecs.values())
    print(f"=== Video Technical Summary ({total} streams) ===\n")

    print("Codecs:")
    for k, v in codecs.most_common():
        print(f"  {k}: {v} ({v/total*100:.0f}%)")

    print("\nResolutions:")
    for k, v in resolutions.most_common():
        print(f"  {k}: {v}")

    print("\nColor Spaces:")
    for k, v in color_spaces.most_common():
        print(f"  {k}: {v}")

    print("\nColor Transfers:")
    for k, v in color_transfers.most_common():
        print(f"  {k}: {v}")

    print("\nPixel Formats:")
    for k, v in pix_fmts.most_common():
        print(f"  {k}: {v}")

    print("\nBit Depths:")
    for k, v in depths.most_common():
        print(f"  {k}: {v}")

    print("\nFrame Rates:")
    for k, v in sorted(framerates.items()):
        print(f"  {k}fps: {v}")

    if outliers:
        print(f"\n=== Resolution Outliers (non-4K) ===\n")
        for i, o in enumerate(outliers, 1):
            print(f"{i}. {o['name']}")
            print(f"   {o['res']} | {o['codec']} | {o['color_space']}")
            print(f"   {o['path']}")
            print()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <analysis_root>")
        print("Example: python extract-technical-report.py C:\\Users\\...\\davinci-resolve-mcp-analysis\\project-2aadc4a565")
        sys.exit(1)
    main(sys.argv[1])
