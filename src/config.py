"""集中配置 — 所有可调参数都在这个文件里, 手动修改这里即可。

按功能分区: 窗口 / 场景 / 猪 / 时钟。
"""

# ===================== 窗口 =====================
SCREEN_W, SCREEN_H = 320, 240

# ===================== 场景 (草地 / 树) =====================
GROUND_TOP = 175  # 草地顶部 / 地面线 (猪的活动地面)

GRASS_BASE = (111, 154, 73)
GRASS_LIGHT = (133, 173, 67)
GRASS_DARK = (85, 134, 25)
GRASS_HIGHLIGHT = (155, 186, 65)
GRASS_EDGE = (54, 101, 18)

# 3 棵树
#   x        : 树的水平位置
#   scale    : 缩放倍率 (1.0 = 原尺寸, 0.5 = 远景)
#   y_offset : 垂直偏移, 正值向下 (树根扎进草地更深), 负值向上
TREES = [
    {"x": 8,   "scale": 1.0, "y_offset": 32},  # 近景大树
    {"x": 168, "scale": 1.0, "y_offset": 32},  # 近景大树
    {"x": 240, "scale": 0.5, "y_offset": 16},  # 远景小树
]

# ===================== 猪 =====================
GRAVITY = 600.0         # 重力加速度 (px/s^2)
SPAWN_Y = -40           # 生成时脚底 y 坐标 (屏幕上方外侧)
# 渲染额外下移量范围 (每只猪随机取值, 制造高低错落, 避免排成一条直线)
RENDER_Y_OFFSET_MIN = 4
RENDER_Y_OFFSET_MAX = 55

WALK_SPEED = 10.0       # 行走速度 (px/s)
MIN_X = 28              # 活动范围左边界
MAX_X = SCREEN_W - 28   # 活动范围右边界
ANIM_FRAME_TIME = 0.3  # 每帧动画时长 (秒)
FRAME_COUNT = 4         # 每个方向动画帧数

TURN_CHANCE = 0.35      # 随机决策中"转向"的概率
REST_CHANCE = 0.20      # 随机决策中"停下休息"的概率
EAT_CHANCE = 0.20       # 随机决策中"吃草"的概率 (其余概率为继续走)
DECISION_MIN, DECISION_MAX = 1.5, 4.0  # 每次随机决策的间隔范围 (秒)
IDLE_MIN, IDLE_MAX = 1.0, 5.0          # 停下休息的时长范围 (秒)
EAT_LOOPS_MIN, EAT_LOOPS_MAX = 1, 3    # 吃草动画循环次数范围 (每次吃草循环 N 口)

MAX_PIGS = 11           # 猪数量上限 (达到后再次点击触发清屏闪电)

# ===================== 清屏闪电 =====================
LIGHTNING_DURATION = 0.9           # 闪电动画总时长 (秒)
LIGHTNING_BLINKS = 3               # 闪烁次数
LIGHTNING_COLOR = (255, 255, 230)  # 闪电颜色
LIGHTNING_WIDTH = 4                # 闪电线条宽度
LIGHTNING_FLASH_ALPHA = 180        # 屏幕白闪强度 (0-255)

# ===================== 时钟 =====================
CLOCK_ON = (40, 42, 52)          # 点亮段颜色
CLOCK_OFF = (206, 219, 236)      # 未点亮段颜色 (LCD 残影)
CLOCK_BIG = (30, 60, 7)          # 时/分 数字 (宽, 高, 段厚)
CLOCK_SMALL = (15, 30, 4)        # 秒 数字
CLOCK_GAP = 6                    # 数字间距
CLOCK_COLON_W = 16               # 冒号占宽
CLOCK_PANEL_PAD = 16             # 面板内边距
CLOCK_PANEL_BG = (255, 255, 255, 150)  # 面板背景 (半透明白)
CLOCK_PANEL_BORDER = (52, 58, 70, 220)  # 面板边框
