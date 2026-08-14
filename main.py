"""Piggy Meadow — 入口。"""

import pygame

from src.assets import load_assets
from src.clock import Clock
from src.config import SCREEN_W, SCREEN_H, MAX_PIGS
from src.lightning import Lightning
from src.pig import Pig, spawn_position
from src.scene import Scene


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Piggy Meadow")
    fps = pygame.time.Clock()

    assets = load_assets()
    scene = Scene(assets)
    clock = Clock()
    lightning = Lightning()
    pigs = []

    running = True
    while running:
        dt = min(fps.tick(60) / 1000.0, 0.05)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if lightning.active:
                    continue  # 闪电播放中忽略点击
                if len(pigs) >= MAX_PIGS:
                    pigs.clear()
                    lightning.trigger()
                else:
                    x = spawn_position(event.pos[0])
                    pigs.append(Pig(assets, x))

        for pig in pigs:
            pig.update(dt)
        lightning.update(dt)

        scene.draw(screen)
        # 透视排序: 视觉底部 y 小 (远) 的先画, 大 (近) 的后画覆盖其上。
        # 猪最多 MAX_PIGS 只且落地后 sort_key 稳定, Timsort 对近乎有序列表为 O(n), 开销可忽略。
        pigs.sort(key=lambda p: p.sort_key)
        for pig in pigs:
            pig.draw(screen)
        lightning.draw(screen)
        clock.draw(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
