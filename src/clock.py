"""时钟 UI — 七段数码管显示 (Game & Watch 风格)。"""
import time

import pygame

from src.config import (
    CLOCK_ON, CLOCK_OFF, CLOCK_BIG, CLOCK_SMALL,
    CLOCK_GAP, CLOCK_COLON_W, CLOCK_PANEL_PAD,
    CLOCK_PANEL_BG, CLOCK_PANEL_BORDER, GROUND_TOP,
)

# 每个数字点亮的段
SEGMENTS = {
    '0': 'abcdef',
    '1': 'bc',
    '2': 'abged',
    '3': 'abgcd',
    '4': 'fgbc',
    '5': 'afgcd',
    '6': 'afgecd',
    '7': 'abc',
    '8': 'abcdefg',
    '9': 'abcdfg',
}


def _segment_polys(w, h, t):
    """按数字尺寸构建 7 个段的梯形多边形顶点 (坐标含 0..w-1 / 0..h-1)。"""
    hm = (h - t) // 2  # 中段顶部 y
    W, H = w - 1, h - 1
    return {
        'a': [(t, 0), (W - t, 0), (W, t), (0, t)],
        'g': [(t, hm), (W - t, hm), (W, hm + t), (0, hm + t)],
        'd': [(0, H - t), (W, H - t), (W - t, H), (t, H)],
        'f': [(0, t), (t, 0), (t, hm), (0, hm + t)],
        'e': [(0, hm), (t, hm + t), (t, H), (0, H - t)],
        'b': [(W - t, 0), (W, t), (W, hm + t), (W - t, hm)],
        'c': [(W - t, hm + t), (W, hm), (W, H - t), (W - t, H)],
    }


_digit_cache = {}


def _digit_surface(char, w, h, t, on, off):
    key = (char, w, h, t, on, off)
    if key in _digit_cache:
        return _digit_cache[key]
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    polys = _segment_polys(w, h, t)
    for pts in polys.values():
        pygame.draw.polygon(surf, off, pts)          # 未点亮段 (LCD 残影)
    for seg in SEGMENTS.get(char, ''):
        pygame.draw.polygon(surf, on, polys[seg])    # 点亮段
    _digit_cache[key] = surf
    return surf


class Clock:
    def __init__(self):
        self.on = CLOCK_ON
        self.off = CLOCK_OFF
        self.big = CLOCK_BIG     # 时/分 数字 (宽, 高, 段厚)
        self.small = CLOCK_SMALL   # 秒 数字
        self.gap = CLOCK_GAP
        self.colon_w = CLOCK_COLON_W
        self.panel_pad = CLOCK_PANEL_PAD
        self._panel = None
        self._panel_key = None

    def _digit(self, char, size):
        return _digit_surface(char, *size, self.on, self.off)

    def _draw_colon(self, target, x, cy, blink, size):
        w, h, t = size
        dot = t
        if blink:
            color = self.on
        else:
            color = self.off
        pygame.draw.rect(target, color, (x, cy + h // 4 - dot // 2, dot, dot))
        pygame.draw.rect(target, color, (x, cy + 3 * h // 4 - dot // 2, dot, dot))

    def _ensure_panel(self, w, h):
        key = (w, h)
        if self._panel_key == key:
            return
        self._panel = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(self._panel, CLOCK_PANEL_BG,
                         (0, 0, w, h), border_radius=14)
        pygame.draw.rect(self._panel, CLOCK_PANEL_BORDER,
                         (0, 0, w, h), width=2, border_radius=14)
        self._panel_key = key

    def draw(self, target):
        now = time.localtime()
        blink = now.tm_sec % 2 == 0
        hh, mm, ss = (f"{now.tm_hour:02d}", f"{now.tm_min:02d}",
                      f"{now.tm_sec:02d}")

        bw, bh, _ = self.big
        sw, sh, _ = self.small

        main_w = bw * 4 + self.gap * 4 + self.colon_w
        sec_w = sw * 2 + self.gap
        panel_w = max(main_w, sec_w) + self.panel_pad * 2
        panel_h = bh + sh + 12 + self.panel_pad * 2

        # 面板居中, 时间主体位于天空区域 (草地从 GROUND_TOP 开始)
        panel_x = (target.get_width() - panel_w) // 2
        panel_y = (GROUND_TOP - panel_h) // 2
        self._ensure_panel(panel_w, panel_h)
        target.blit(self._panel, (panel_x, panel_y))

        # 主体 HH:MM
        main_x = panel_x + self.panel_pad
        main_y = panel_y + self.panel_pad
        x = main_x
        for i, ch in enumerate(hh + mm):
            if i == 2:
                self._draw_colon(target, x, main_y, blink, self.big)
                x += self.colon_w
            target.blit(self._digit(ch, self.big), (x, main_y))
            x += bw
            if i != 3:
                x += self.gap

        # 秒 (小号, 主体下方居中)
        sec_x = panel_x + (panel_w - sec_w) // 2
        sec_y = main_y + bh + 12
        for i, ch in enumerate(ss):
            target.blit(self._digit(ch, self.small), (sec_x, sec_y))
            sec_x += sw + self.gap
