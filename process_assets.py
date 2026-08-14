#!/usr/bin/env python3
"""P0 资源处理脚本 — 将 assets/ 中的原始精灵表处理为游戏可用的独立 PNG + JSON 元数据。

输入:
  assets/pig_walk.png           512x512 RGBA 4x4 精灵表 (行=朝向, 列=动画帧)
  assets/pig_eat.png            512x512 RGBA 4x4 精灵表
  assets/trees-and-bushes.png   288x160 RGB 场景图 (绿色背景需透明化)

输出 (processed/):
  pig/walk_{left,right}_{0-3}.png    8 帧行走动画
  pig/eat_{left,right}_{0-3}.png     8 帧吃草动画
  scenery/tree.png                   单棵完整大树 (透明背景)
  sprites.json                       帧尺寸 + 锚点偏移元数据

用法:
  python process_assets.py
"""

import json
from pathlib import Path
from PIL import Image

ASSETS_DIR = Path("assets")
OUTPUT_DIR = Path("processed")

BG_COLOR = (101, 141, 65)   # trees-and-bushes.png 的背景 key color
BG_TOLERANCE = 15           # 背景匹配容差

CELL_SIZE = 128             # 精灵表每格尺寸
GRID_COLS = 4               # 精灵表每行帧数
PIG_ROWS = {1: "left", 3: "right"}  # 仅保留左右侧面方向
FRAMES = 4                  # 每个方向的动画帧数

ANCHOR_X = CELL_SIZE // 2   # 锚点 x = 格子水平中心 (转向时猪不跳位)


def is_background(rgb):
    """判断像素是否属于背景 key color (含容差)。"""
    return all(abs(rgb[c] - BG_COLOR[c]) <= BG_TOLERANCE for c in range(3))


def extract_pig_frames(src_path, anim_name):
    """从 4x4 精灵表提取 left/right 方向的 4 帧, 返回元数据列表。"""
    img = Image.open(src_path).convert("RGBA")
    frames = {"left": [], "right": []}

    for row, direction in PIG_ROWS.items():
        for col in range(FRAMES):
            box = (col * CELL_SIZE, row * CELL_SIZE,
                   (col + 1) * CELL_SIZE, (row + 1) * CELL_SIZE)
            cell = img.crop(box)

            bbox = cell.getbbox()
            if bbox is None:
                raise RuntimeError(
                    f"{src_path.name}: 格子({row},{col}) 无内容, 精灵表布局可能不符预期")
            x0, y0, x1, y1 = bbox  # x1, y1 为排他边界

            frame = cell.crop(bbox)

            anchor_x = ANCHOR_X
            anchor_y = y1 - 1            # 排他边界减一 = 脚底行
            offset_x = x0 - anchor_x
            offset_y = y0 - anchor_y

            fname = f"{anim_name}_{direction}_{col}.png"
            frame.save(OUTPUT_DIR / "pig" / fname)

            frames[direction].append({
                "file": f"pig/{fname}",
                "w": frame.width,
                "h": frame.height,
                "offset_x": offset_x,
                "offset_y": offset_y,
            })

    return frames


def extract_tree():
    """从 trees-and-bushes.png 提取一棵完整大树 (背景透明化 + 列密度分析)。

    策略: 背景色透明化后, 逐列统计非透明像素数; 密度骤降的列为树间空隙;
    取两块空隙之间的区域, 且优先选择不触及图片边缘的完整树。
    """
    img = Image.open(ASSETS_DIR / "trees-and-bushes.png").convert("RGBA")
    w, h = img.size
    px = img.load()

    # 1. 背景透明化
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if is_background((r, g, b)):
                px[x, y] = (r, g, b, 0)

    # 2. 逐列非透明像素密度
    col_density = [sum(1 for y in range(h) if px[x, y][3] > 0)
                   for x in range(w)]

    max_density = max(col_density)
    threshold = max(30, int(max_density * 0.2))

    # 3. 找空隙列 (密度低于阈值), 连续空隙取中点
    gaps = [x for x in range(1, w - 1) if col_density[x] < threshold]
    splits = []
    if gaps:
        start = gaps[0]
        prev = gaps[0]
        for g in gaps[1:]:
            if g == prev + 1:
                prev = g
            else:
                splits.append((start + prev) // 2)
                start = g
                prev = g
        splits.append((start + prev) // 2)

    # 4. 由空隙中点切分区域
    regions = []
    prev = -1
    for s in splits:
        regions.append((prev + 1, s - 1))
        prev = s
    regions.append((prev + 1, w - 1))
    regions = [(a, b) for (a, b) in regions if b - a >= 20]

    # 5. 优先选择不触及图片边缘的完整区域 (树), 否则取最宽
    candidates = [(a, b) for (a, b) in regions if a > 0 and b < w - 1]
    if not candidates:
        candidates = regions
    x0, x1 = max(candidates, key=lambda r: r[1] - r[0])

    tree = img.crop((x0, 0, x1 + 1, h))
    bbox = tree.getbbox()
    tree = tree.crop(bbox)

    fname = "tree.png"
    tree.save(OUTPUT_DIR / "scenery" / fname)

    return {"file": f"scenery/{fname}", "w": tree.width, "h": tree.height}


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    (OUTPUT_DIR / "pig").mkdir(exist_ok=True)
    (OUTPUT_DIR / "scenery").mkdir(exist_ok=True)

    metadata = {
        "pig": {},
        "scenery": {},
        "background_key_color": list(BG_COLOR),
        "cell_size": CELL_SIZE,
        "anchor_x": ANCHOR_X,
    }

    metadata["pig"]["walk"] = extract_pig_frames(
        ASSETS_DIR / "pig_walk.png", "walk")
    metadata["pig"]["eat"] = extract_pig_frames(
        ASSETS_DIR / "pig_eat.png", "eat")

    metadata["scenery"]["tree"] = extract_tree()

    with open(OUTPUT_DIR / "sprites.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    # 汇总输出
    pig_files = sorted((OUTPUT_DIR / "pig").glob("*.png"))
    tree_files = sorted((OUTPUT_DIR / "scenery").glob("*.png"))
    print(f"输出目录: {OUTPUT_DIR.resolve()}")
    print(f"猪精灵帧: {len(pig_files)} 个")
    for p in pig_files:
        print(f"  {p.name}")
    print(f"场景精灵: {len(tree_files)} 个")
    for p in tree_files:
        print(f"  {p.name}")
    print(f"元数据:   sprites.json")

    # 锚点一致性检查 (同方向各帧 offset 应接近)
    print("\n锚点一致性检查 (offset_x, offset_y):")
    for anim, dirs in metadata["pig"].items():
        for direction, frames in dirs.items():
            offsets = [(f["offset_x"], f["offset_y"]) for f in frames]
            uniq_x = {ox for ox, _ in offsets}
            uniq_y = {oy for _, oy in offsets}
            status = "OK" if len(uniq_x) == 1 and len(uniq_y) == 1 else "WARN"
            print(f"  {anim:>4}/{direction:<5} {offsets}  {status}")


if __name__ == "__main__":
    main()
