# Piggy Meadow — 资源分析报告 (P-1)

> 供 coding 模型直接使用的精灵表结构化描述

---

## 1. pig_walk.png — 行走动画精灵表

**文件**: `assets/pig_walk.png` | **尺寸**: 512×512 | **格式**: RGBA (带透明通道) | **网格**: 4行 × 4列 = 16格 | **每格**: 128×128px

### 布局规则: 行=朝向, 列=动画帧

| 行 | 朝向 | 精灵尺寸(裁切后) | 描述 |
|----|------|-----------------|------|
| **Row 0** | 背面 (Back) | ~21×47px | 猪背对镜头，可见尾巴和后背，4帧行走循环 |
| **Row 1** | 左侧 (Left) | ~55×30px | 猪侧面朝左，4帧行走循环（腿步态变化） |
| **Row 2** | 正面 (Front) | ~21×45px | 猪正对镜头，4帧行走循环 |
| **Row 3** | 右侧 (Right) | ~55×30px | 猪侧面朝右，4帧行走循环（腿步态变化） |

### 关键发现
- **Row 1 和 Row 3 是水平镜像关系** — Row 1 面左，Row 3 面右
- **Row 0 和 Row 2 是竖直视角** — 背面/正面，尺寸窄高 (~21×47)
- **Row 1 和 Row 3 是侧面视角** — 尺寸宽矮 (~55×30)
- 每行 4 帧构成一个完整的行走循环动画
- 原始像素很小（21~57px），游戏内需要放大 2~4 倍使用

### 编码引用格式
```
pig_walk[row][col]  row ∈ {0,1,2,3}  col ∈ {0,1,2,3}
方向映射:
  0 = back   (背面)
  1 = left   (左侧)
  2 = front  (正面)
  3 = right  (右侧)
```

---

## 2. pig_eat.png — 吃东西动画精灵表

**文件**: `assets/pig_eat.png` | **尺寸**: 512×512 | **格式**: RGBA (带透明通道) | **网格**: 4行 × 4列 = 16格 | **每格**: 128×128px

### 布局规则: 同 walk, 行=朝向, 列=动画帧

| 行 | 朝向 | 精灵尺寸(裁切后) | 描述 |
|----|------|-----------------|------|
| **Row 0** | 背面 (Back) | ~21×42px | 猪背面低头吃草，头逐渐低下再抬起 |
| **Row 1** | 左侧 (Left) | ~55×30px | 猪左侧低头吃草，头部向下摆动 |
| **Row 2** | 正面 (Front) | ~21×46px | 猪正面低头吃草 |
| **Row 3** | 右侧 (Right) | ~55×30px | 猪右侧低头吃草 |

### 与 walk 的对比
- eat 的 Row 1 后两帧 (col 2,3) 头部更低，更明显地"低头"
- eat 的 Row 0/Row 2 帧高度略有变化（低头动作导致）
- **同样存在 Row 1↔Row 3 镜像关系**

### 编码引用格式
```
pig_eat[row][col]  row ∈ {0,1,2,3}  col ∈ {0,1,2,3}
方向映射同上
```

---

## 3. trees-and-bushes.png — 场景装饰图块集

**文件**: `assets/trees-and-bushes.png` | **尺寸**: 288×160 | **格式**: RGB (**无透明通道**) | **颜色数**: 35色

### 背景 Key Color
```
RGB(101, 141, 65)  —  橄榄绿草地背景色，占 10379 像素 (22.5%)
容差建议: ±15 用于透明化处理
```

### 包含的独立精灵 (从左到右, 从上到下)

| # | 类型 | 大约位置 | 描述 | 用途 |
|---|------|---------|------|------|
| A | 大圆树 | 左侧 x:0-140 y:0-155 | 宽大圆形树冠 + 可见树干 + 底部阴影 | 主场景背景树 |
| B | 大圆树 | 中间 x:145-280 y:0-155 | 同A的变体或镜像 | 主场景背景树 |
| C | 松针树 | 右上角 x:240-275 y:10-70 | 三角形松树轮廓 | 远景装饰 |
| D | 灌木丛 | 右中 x:255-280 y:75-100 | 小圆形灌木 | 地面装饰 |
| E | 小花/草 | 右下散布 x:230-288 y:105-160 | 多个小像素团块 | 地面细节 |

### 颜色调色板 (主要颜色)
```
草地系 (背景+前景):
  (101, 141, 65) — 背景底色 (需透明化)
  (133, 173, 67) — 浅绿草地高光
  (85, 134, 25)  — 深绿草地阴影
  (111, 154, 73) — 中绿过渡
  (155, 186, 65) — 最浅绿高光

树叶系:
  (54, 101, 18)  — 深绿树叶主色
  (17, 77, 60)   — 暗绿树叶阴影
  (109, 185, 39) — 亮绿树叶高光

树干/暗部:
  (37, 34, 46)   — 深灰褐树干
  (49, 79, 69)   — 暗绿阴影
  (61, 63, 55)   — 灰色阴影
```

### 处理要求
1. **必须添加 Alpha 通道** — 将 `RGB(101,141,65)` ±15 容差设为 transparent
2. **可按区域裁切为独立 PNG** — 方便游戏中按需放置
3. **建议输出尺寸** — 保持原始像素比例，由渲染层决定缩放

---

## 4. 综合处理规格表 (供 P0 资源处理脚本使用)

```typescript
// === 精灵表裁切配置 ===
interface SpriteSheetConfig {
  source: string;
  gridSize: { cols: number; rows: number };      // 4x4
  cellSize: { w: number; h: number };             // 128x128
  trim: boolean;                                  // true = 裁切到内容边界
  outputPrefix: string;
}

const WALK_CONFIG: SpriteSheetConfig = {
  source: "assets/pig_walk.png",
  gridSize: { cols: 4, rows: 4 },
  cellSize: { w: 128, h: 128 },
  trim: true,
  outputPrefix: "walk"
};

const EAT_CONFIG: SpriteSheetConfig = {
  source: "assets/pig_eat.png",
  gridSize: { cols: 4, rows: 4 },
  cellSize: { w: 128, h: 128 },
  trim: true,
  outputPrefix: "eat"
};

// === 方向枚举 ===
enum PigDirection {
  BACK = 0,    // 背面
  LEFT = 1,    // 左侧
  FRONT = 2,   // 正面
  RIGHT = 3    // 右侧
}

// === 动画状态 ===
type PigAnimation = "walk" | "eat";
// 每个 state 有 4 帧 (col 0-3), 循环播放

// === 树木图块配置 ===
interface TreesConfig {
  source: "assets/trees-and-bushes.png";
  bgColor: [number, number, number];  // [101, 141, 65]
  tolerance: number;                   // 15
  addAlpha: boolean;                   // true
  // 可选: 按 bbox 裁切为独立精灵
  sprites?: Array<{
    id: string;
    bbox: [number, number, number, number]; // [x0, y0, x1, y1]
  }>;
}
```

---

## 5. 游戏使用建议

### 猪实体渲染参数
```
默认缩放倍率: 3x 或 4x (原始 21-57px → 游戏内 63-228px)
碰撞盒: 基于裁切后的实际像素边界框
锚点: 底部中心 (foot point)，用于地面对齐
动画帧率: 8-12 FPS (4帧循环 ≈ 333-500ms/周期)
```

### 场景层级建议
```
Layer 0: 天空渐变 (CSS/Canvas 渐变填充)
Layer 1: trees-and-bushes 精灵 A/B (大树, 放在远处)
Layer 2: 草地地面 (纯色或简单纹理)
Layer 3: trees-and-bushes 精灵 C/D/E (小装饰, 近景)
Layer 4: 猪 (walk/eat 动画, 按 Y 排序实现遮挡)
Layer 5: 时钟 UI (七段数码管, 屏幕中央)
Layer 6: Game & Watch 外壳边框 (CSS overlay)
```

### 内存预算 (估算)
```
pig_walk.png:   512×512×4B = 1MB (原始)
pig_eat.png:    512×512×4B = 1MB (原始)
trees.png:      288×160×4B = 185KB (加 alpha 后)
裁切后单帧:     最大 57×30×4B ≈ 6.8KB
全部裁切帧:     32帧 × ~5KB avg ≈ 160KB
总内存占用:     < 5MB (完全可接受)
```
