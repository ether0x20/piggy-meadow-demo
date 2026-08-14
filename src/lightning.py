"""闪电清屏效果 — 猪满员后触发的闪电动画。"""

import random

import pygame

from src.config import (
    SCREEN_W, SCREEN_H, GROUND_TOP,
    LIGHTNING_DURATION, LIGHTNING_BLINKS,
    LIGHTNING_COLOR, LIGHTNING_WIDTH, LIGHTNING_FLASH_ALPHA,
)


def _zigzag(x0, y0, x1, y1, segments, jitter, rng):
    """生成一条锯齿折线 (闪电分支)。"""
    points = [(x0, y0)]
    for i in range(1, segments):
        t = i / segments
        x = x0 + (x1 - x0) * t + rng.uniform(-jitter, jitter)
        y = y0 + (y1 - y0) * t
        points.append((x, y))
    points.append((x1, y1))
    return points


class Lightning:
    def __init__(self):
        self.rng = random.Random()
        self.active = False
        self.timer = 0.0
        self.bolts = []           # 每条闪电的折线点列表
        self._flash = pygame.Surface((SCREEN_W, SCREEN_H))
        self._flash.fill((255, 255, 255))

    def trigger(self):
        self.active = True
        self.timer = 0.0
        self._generate_bolts()

    def _generate_bolts(self):
        rng = self.rng
        # 主闪电: 从屏幕顶部劈到地面
        top_x = rng.uniform(SCREEN_W * 0.3, SCREEN_W * 0.7)
        bot_x = top_x + rng.uniform(-60, 60)
        main = _zigzag(top_x, 0, bot_x, GROUND_TOP, 10, 18, rng)

        bolts = [main]

        # 2-3 条分叉, 从主闪电中段分出
        for _ in range(rng.randint(2, 3)):
            idx = rng.randint(len(main) // 3, len(main) * 2 // 3)
            bx, by = main[idx]
            dir_x = rng.choice((-1, 1))
            branch = _zigzag(bx, by,
                             bx + dir_x * rng.uniform(30, 70),
                             by + rng.uniform(20, GROUND_TOP - by),
                             rng.randint(3, 5), 8, rng)
            bolts.append(branch)

        self.bolts = bolts

    def _is_visible(self):
        blink_interval = LIGHTNING_DURATION / LIGHTNING_BLINKS
        phase = int(self.timer / blink_interval)
        return phase % 2 == 0

    def update(self, dt):
        if not self.active:
            return
        self.timer += dt
        if self.timer >= LIGHTNING_DURATION:
            self.active = False

    def draw(self, target):
        if not self.active or not self._is_visible():
            return
        # 屏幕白闪 (强度随本周期时间衰减)
        blink_interval = LIGHTNING_DURATION / LIGHTNING_BLINKS
        t = self.timer % blink_interval
        alpha = int(LIGHTNING_FLASH_ALPHA * (1 - t / blink_interval))
        self._flash.set_alpha(max(0, alpha))
        target.blit(self._flash, (0, 0))
        # 闪电线条
        for bolt in self.bolts:
            pygame.draw.lines(target, LIGHTNING_COLOR, False, bolt,
                              LIGHTNING_WIDTH)
