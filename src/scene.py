"""场景渲染 — 天空、草地、树木的静态背景层。"""
import random

import pygame

from src.config import (
    SCREEN_W, SCREEN_H, GROUND_TOP,
    GRASS_BASE, GRASS_LIGHT, GRASS_DARK, GRASS_HIGHLIGHT, GRASS_EDGE,
    TREES,
)


class Scene:
    def __init__(self, assets, seed=7):
        self.assets = assets
        self.rng = random.Random(seed)
        self.surface = pygame.Surface((SCREEN_W, SCREEN_H))
        self._render_background()

    def _render_background(self):
        surf = self.surface
        surf.blit(self.assets["sky"], (0, 0))
        self._draw_grass(surf)
        self._draw_trees(surf)

    def _draw_grass(self, surf):
        rng = self.rng
        for y in range(GROUND_TOP, SCREEN_H):
            for x in range(SCREEN_W):
                r = rng.random()
                if r < 0.06:
                    color = GRASS_HIGHLIGHT
                elif r < 0.14:
                    color = GRASS_LIGHT
                elif r < 0.20:
                    color = GRASS_DARK
                else:
                    color = GRASS_BASE
                surf.set_at((x, y), color)
        # 地面顶部高光线
        pygame.draw.line(surf, GRASS_LIGHT, (0, GROUND_TOP), (SCREEN_W, GROUND_TOP))
        # 底部深色边缘
        pygame.draw.rect(surf, GRASS_EDGE, (0, SCREEN_H - 4, SCREEN_W, 4))

    def _draw_trees(self, surf):
        tree = self.assets["tree"]  # 111x160
        for cfg in TREES:
            img = tree if cfg["scale"] == 1.0 else pygame.transform.scale(
                tree, (round(tree.get_width() * cfg["scale"]),
                       round(tree.get_height() * cfg["scale"])))
            y = GROUND_TOP - img.get_height() + cfg["y_offset"]
            surf.blit(img, (cfg["x"], y))

    def draw(self, target):
        target.blit(self.surface, (0, 0))
