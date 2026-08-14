"""猪实体 — 状态机与物理 (下落 → 落地 → 行走/暂停)。"""

import random

from src.config import (
    GRAVITY, SPAWN_Y, RENDER_Y_OFFSET_MIN, RENDER_Y_OFFSET_MAX, GROUND_TOP,
    WALK_SPEED, MIN_X, MAX_X, ANIM_FRAME_TIME, FRAME_COUNT,
    TURN_CHANCE, REST_CHANCE, EAT_CHANCE,
    DECISION_MIN, DECISION_MAX, IDLE_MIN, IDLE_MAX,
    EAT_LOOPS_MIN, EAT_LOOPS_MAX,
)


class Pig:
    FALLING = "falling"
    WALKING = "walking"
    IDLE = "idle"
    EATING = "eating"

    def __init__(self, assets, x, direction=None):
        self.assets = assets
        self.rng = random.Random()
        self.x = float(x)
        self.y = float(SPAWN_Y)
        self.vy = 0.0
        self.direction = direction or self.rng.choice(("left", "right"))
        self.state = self.FALLING
        # 每只猪随机下移量, 制造草地高低错落
        self.render_y_offset = self.rng.randint(RENDER_Y_OFFSET_MIN,
                                                RENDER_Y_OFFSET_MAX)

        self.frame_index = 0
        self.anim_timer = 0.0
        self.state_timer = 0.0
        self.decision_interval = 0.0
        self.idle_duration = 0.0
        self.eat_loops = 0
        self.loops_done = 0

    # ---------- 更新 ----------

    def update(self, dt):
        if self.state == self.FALLING:
            self._update_falling(dt)
        elif self.state == self.WALKING:
            self._update_walking(dt)
        elif self.state == self.IDLE:
            self._update_idle(dt)
        elif self.state == self.EATING:
            self._update_eating(dt)

    def _update_falling(self, dt):
        self.vy += GRAVITY * dt
        self.y += self.vy * dt
        if self.y >= GROUND_TOP:
            self.y = GROUND_TOP
            self.vy = 0.0
            self._start_walking()

    def _update_walking(self, dt):
        self.state_timer += dt

        dx = -WALK_SPEED if self.direction == "left" else WALK_SPEED
        self.x += dx * dt

        # 屏幕边缘转向
        if self.x <= MIN_X:
            self.x = MIN_X
            self.direction = "right"
        elif self.x >= MAX_X:
            self.x = MAX_X
            self.direction = "left"

        # 动画帧推进
        self.anim_timer += dt
        if self.anim_timer >= ANIM_FRAME_TIME:
            self.anim_timer -= ANIM_FRAME_TIME
            self.frame_index = (self.frame_index + 1) % FRAME_COUNT

        # 随机行为决策
        if self.state_timer >= self.decision_interval:
            self._make_decision()

    def _update_idle(self, dt):
        self.state_timer += dt
        if self.state_timer >= self.idle_duration:
            self._start_walking()

    def _update_eating(self, dt):
        # 吃草动画帧推进, 每完成一轮 (4 帧) 记一口
        self.anim_timer += dt
        if self.anim_timer >= ANIM_FRAME_TIME:
            self.anim_timer -= ANIM_FRAME_TIME
            self.frame_index += 1
            if self.frame_index >= FRAME_COUNT:
                self.frame_index = 0
                self.loops_done += 1
                if self.loops_done >= self.eat_loops:
                    self._start_walking()

    # ---------- 状态切换 ----------

    def _start_walking(self):
        self.state = self.WALKING
        self.state_timer = 0.0
        self.decision_interval = self.rng.uniform(DECISION_MIN, DECISION_MAX)

    def _start_idle(self):
        self.state = self.IDLE
        self.state_timer = 0.0
        self.idle_duration = self.rng.uniform(IDLE_MIN, IDLE_MAX)
        self.frame_index = 0  # 站立帧

    def _start_eating(self):
        self.state = self.EATING
        self.eat_loops = self.rng.randint(EAT_LOOPS_MIN, EAT_LOOPS_MAX)
        self.loops_done = 0
        self.frame_index = 0
        self.anim_timer = 0.0

    def _make_decision(self):
        self.state_timer = 0.0
        self.decision_interval = self.rng.uniform(DECISION_MIN, DECISION_MAX)
        r = self.rng.random()
        if r < TURN_CHANCE:
            # 转向
            self.direction = "right" if self.direction == "left" else "left"
        elif r < TURN_CHANCE + REST_CHANCE:
            # 停下休息
            self._start_idle()
        elif r < TURN_CHANCE + REST_CHANCE + EAT_CHANCE:
            # 吃草
            self._start_eating()

    # ---------- 渲染 ----------

    @property
    def sort_key(self):
        """视觉底部 y 坐标 (用于透视排序: 值越大越靠前, 越应绘制在顶层)。"""
        return self.y + self.render_y_offset

    def _current_frame(self):
        if self.state == self.IDLE:
            return self.assets["pig"]["walk"][self.direction][0]
        anim = "eat" if self.state == self.EATING else "walk"
        return self.assets["pig"][anim][self.direction][self.frame_index]

    def draw(self, target):
        frame = self._current_frame()
        target.blit(frame["surf"],
                    (round(self.x) + frame["offset_x"],
                     round(self.y) + frame["offset_y"] + self.render_y_offset))


def spawn_position(click_x):
    """将点击 x 限制在屏幕内, 避免猪出生在边缘外。"""
    return max(MIN_X, min(MAX_X, click_x))
