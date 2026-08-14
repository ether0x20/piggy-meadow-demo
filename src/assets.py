"""资源加载 — 从 processed/ 目录加载精灵和元数据。"""
import json
import sys
from pathlib import Path

import pygame


def _base_dir():
    """资源根目录 (兼容 PyInstaller 打包: 打包后资源位于 sys._MEIPASS)。"""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


PROCESSED = _base_dir() / "processed"


def _load(rel_path):
    return pygame.image.load(str(PROCESSED / rel_path)).convert_alpha()


def load_icon():
    """窗口/任务栏图标 (运行时, PyInstaller --icon 只影响 exe 文件图标)。"""
    return pygame.image.load(str(PROCESSED / "icon.png"))


def load_assets():
    meta = json.loads((PROCESSED / "sprites.json").read_text(encoding="utf-8"))

    pig = {}
    for anim in ("walk", "eat"):
        pig[anim] = {}
        for direction in ("left", "right"):
            frames = []
            for f in meta["pig"][anim][direction]:
                frames.append({
                    "surf": _load(f["file"]),
                    "offset_x": f["offset_x"],
                    "offset_y": f["offset_y"],
                })
            pig[anim][direction] = frames

    tree = _load(meta["scenery"]["tree"]["file"])

    sky = _load("scenery/sky.png")  # 640x480 (2x 生成)
    if sky.get_size() != (320, 240):
        sky = pygame.transform.scale(sky, (320, 240))  # 精确 2x 最近邻降采样

    return {
        "pig": pig,
        "tree": tree,
        "sky": sky,
        "meta": meta,
    }
