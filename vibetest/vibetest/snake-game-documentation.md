# 贪吃蛇游戏开发文档

## 目录

1. [项目概述](#项目概述)
2. [技术选型与架构设计](#技术选型与架构设计)
3. [核心模块实现详解](#核心模块实现详解)
4. [高级功能实现](#高级功能实现)
5. [问题与解决方案](#问题与解决方案)
6. [项目结构](#项目结构)
7. [代码参考](#代码参考)

---

## 项目概述

本项目是一个功能完整的贪吃蛇游戏，采用纯前端技术（HTML5 Canvas + JavaScript + CSS3）实现。游戏支持多种地图尺寸、预设障碍地图、动态形状化障碍、难度选择、颜色主题等高级功能。

### 功能特性

| 功能模块 | 描述 |
|---------|------|
| 基础游戏 | 蛇的移动、食物收集、碰撞检测 |
| 地图系统 | 小/中/大三种尺寸，可选预设障碍 |
| 动态障碍 | 6种形状，带预警提示 |
| 难度系统 | 4个难度等级，影响速度和得分 |
| 主题系统 | 随机颜色生成，支持实时切换 |
| 分数系统 | 实时得分、本次最高分记录 |

---

## 技术选型与架构设计

### 2.1 技术栈

| 技术 | 用途 | 选型理由 |
|-----|------|---------|
| HTML5 Canvas | 游戏画面渲染 | 高性能2D绘图，适合游戏开发 |
| 原生 JavaScript | 游戏逻辑 | 无需框架依赖，轻量高效 |
| CSS3 | UI样式和动画 | 丰富的视觉效果支持 |
| 单文件架构 | 项目组织 | 便于部署，无需构建工具 |

### 2.2 游戏架构

采用经典的游戏循环模式：

```
┌─────────────────────────────────────────┐
│              游戏初始化                  │
│  (初始化变量、生成食物、启动游戏循环)      │
└─────────────────┬───────────────────────┘
                  ▼
┌─────────────────────────────────────────┐
│              游戏循环                    │
│  ┌─────────┐    ┌─────────┐            │
│  │  update │───▶│  draw   │            │
│  │ (更新)  │    │ (渲染)  │            │
│  └─────────┘    └─────────┘            │
│       │              │                  │
│       ▼              ▼                  │
│  检测碰撞      绘制游戏画面              │
│  更新位置      绘制蛇、食物、障碍        │
└─────────────────┬───────────────────────┘
                  │
         游戏结束？────是────▶ 显示结束界面
                  │否
                  ▼
              继续循环
```

### 2.3 核心状态机

```javascript
// 游戏状态变量
let gameRunning = false;   // 游戏是否进行中
let gamePaused = false;    // 游戏是否暂停
let score = 0;            // 当前分数
let sessionHighScore = 0; // 本次最高分
```

**状态转换表：**

| 当前状态 | 事件 | 新状态 | 操作 |
|---------|------|--------|------|
| 初始 | 点击开始 | 运行中 | 启动游戏循环 |
| 运行中 | 按空格 | 暂停 | 停止更新 |
| 暂停 | 按空格 | 运行中 | 恢复更新 |
| 运行中 | 碰撞 | 结束 | 显示结束界面 |
| 结束 | 重新开始 | 运行中 | 重置并启动 |

---

## 核心模块实现详解

### 3.1 蛇的数据结构与移动

#### 数据结构

```javascript
// 蛇身数组，头部在索引0
let snake = [{ x: 10, y: 10 }];

// 速度向量
let velocity = { x: 0, y: 0 };     // 当前速度
let nextVelocity = { x: 0, y: 0 }; // 下一帧速度（缓冲）
```

#### 移动算法

```javascript
function update() {
    // 应用缓冲的速度
    velocity = { x: nextVelocity.x, y: nextVelocity.y };
    
    // 如果还没开始移动，不更新
    if (velocity.x === 0 && velocity.y === 0) return;
    
    // 计算新头部位置
    const head = {
        x: snake[0].x + velocity.x,
        y: snake[0].y + velocity.y
    };
    
    // 添加新头部
    snake.unshift(head);
    
    // 检测是否吃到食物
    if (food && head.x === food.x && head.y === food.y) {
        // 吃到食物：增加分数，生成新食物
        score += 10;
        food = generateFood();
        // 注意：不删除尾部，蛇增长
    } else {
        // 没吃到食物：删除尾部，实现移动效果
        snake.pop();
    }
}
```

#### 方向控制

```javascript
document.addEventListener('keydown', (e) => {
    switch(e.key) {
        case 'ArrowUp':
            // 防止180度转向（不能从向上直接变成向下）
            if (velocity.y === 0) {
                nextVelocity = { x: 0, y: -1 };
            }
            break;
        case 'ArrowDown':
            if (velocity.y === 0) {
                nextVelocity = { x: 0, y: 1 };
            }
            break;
        case 'ArrowLeft':
            if (velocity.x === 0) {
                nextVelocity = { x: -1, y: 0 };
            }
            break;
        case 'ArrowRight':
            if (velocity.x === 0) {
                nextVelocity = { x: 1, y: 0 };
            }
            break;
    }
});
```

### 3.2 碰撞检测系统

#### 检测类型

| 碰撞类型 | 检测方法 | 处理方式 |
|---------|---------|---------|
| 撞墙 | 坐标边界检查 | 游戏结束 |
| 撞自己 | 与蛇身数组比较 | 游戏结束 |
| 撞障碍 | 与障碍物数组比较 | 游戏结束 |
| 吃食物 | 坐标相等 | 增长+加分 |

#### 实现代码

```javascript
function checkCollisions(head) {
    // 1. 撞墙检测
    if (head.x < 0 || head.x >= tileCountX || 
        head.y < 0 || head.y >= tileCountY) {
        gameOver();
        return true;
    }
    
    // 2. 撞自己检测
    // 从索引1开始，排除头部自身
    for (let i = 1; i < snake.length; i++) {
        if (snake[i].x === head.x && snake[i].y === head.y) {
            gameOver();
            return true;
        }
    }
    
    // 3. 撞障碍物检测
    for (let obs of obstacles) {
        if (obs.x === head.x && obs.y === head.y) {
            gameOver();
            return true;
        }
    }
    
    return false;
}
```

### 3.3 食物生成系统

#### 生成算法

```javascript
function generateFood() {
    let newFood;
    let attempts = 0;
    const maxAttempts = 1000;
    
    do {
        newFood = {
            x: Math.floor(Math.random() * tileCountX),
            y: Math.floor(Math.random() * tileCountY)
        };
        attempts++;
        
        // 防止无限循环（地图满时）
        if (attempts > maxAttempts) {
            console.warn('无法生成食物，地图可能已满');
            return null;
        }
    } while (
        // 检查是否与蛇身重叠
        isSnakeAt(newFood.x, newFood.y) || 
        // 检查是否与障碍物重叠
        isObstacleAt(newFood.x, newFood.y)
    );
    
    return newFood;
}
```

### 3.4 游戏渲染系统

#### 渲染流程

```javascript
function draw() {
    // 1. 清空画布
    ctx.fillStyle = '#0a0a0a';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // 2. 绘制网格背景
    drawGrid();
    
    // 3. 绘制障碍物
    drawObstacles();
    
    // 4. 绘制蛇
    drawSnake();
    
    // 5. 绘制食物
    drawFood();
    
    // 6. 绘制暂停提示（如需要）
    if (gamePaused) {
        drawPauseScreen();
    }
}
```

#### 蛇的绘制（带渐变效果）

```javascript
function drawSnake() {
    snake.forEach((segment, index) => {
        if (index === 0) {
            // 头部：发光效果
            ctx.fillStyle = snakeColor;
            ctx.shadowBlur = 10;
            ctx.shadowColor = snakeColor;
        } else {
            // 身体：渐变透明度
            ctx.fillStyle = snakeColor;
            ctx.globalAlpha = Math.max(0.4, 1 - index * 0.05);
            ctx.shadowBlur = 0;
        }
        
        ctx.fillRect(
            segment.x * gridSize + 1,
            segment.y * gridSize + 1,
            gridSize - 2,
            gridSize - 2
        );
        
        ctx.globalAlpha = 1; // 重置透明度
    });
}
```

#### 食物绘制（发光效果）

```javascript
function drawFood() {
    if (!food) return;
    
    ctx.fillStyle = foodColor;
    ctx.shadowBlur = 15;
    ctx.shadowColor = foodColor;
    
    // 绘制圆形食物
    ctx.beginPath();
    ctx.arc(
        food.x * gridSize + gridSize / 2,
        food.y * gridSize + gridSize / 2,
        gridSize / 2 - 2,
        0,
        Math.PI * 2
    );
    ctx.fill();
    
    ctx.shadowBlur = 0; // 重置阴影
}
```

### 3.5 游戏循环实现

```javascript
let gameLoopId = null;
let gameSpeed = 100; // 毫秒/帧

function startGameLoop() {
    // 清除现有循环
    if (gameLoopId) {
        clearInterval(gameLoopId);
    }
    
    // 启动新循环
    gameLoopId = setInterval(() => {
        if (!gamePaused) {
            update(); // 更新游戏状态
        }
        draw();     // 渲染画面
    }, gameSpeed);
}

function stopGameLoop() {
    if (gameLoopId) {
        clearInterval(gameLoopId);
        gameLoopId = null;
    }
}
```

### 3.6 分数系统

```javascript
// 难度配置
const difficulties = {
    easy:   { speed: 150, scoreMultiplier: 1 },
    normal: { speed: 100, scoreMultiplier: 1.5 },
    hard:   { speed: 60,  scoreMultiplier: 2 },
    expert: { speed: 40,  scoreMultiplier: 3 }
};

// 得分计算
function addScore() {
    const difficulty = document.getElementById('difficulty').value;
    const multiplier = difficulties[difficulty].scoreMultiplier;
    score += Math.floor(10 * multiplier);
    
    // 更新最高分
    if (score > sessionHighScore) {
        sessionHighScore = score;
        highScoreElement.textContent = sessionHighScore;
    }
    
    scoreElement.textContent = score;
}
```

---

## 高级功能实现

### 4.1 预设障碍地图系统

#### 地图数据结构

```javascript
const presetMaps = [
    {
        name: "十字迷宫",
        getObstacles: (tileCountX, tileCountY) => {
            const obs = [];
            const cx = Math.floor(tileCountX / 2);
            const cy = Math.floor(tileCountY / 2);
            
            // 横向障碍
            for (let x = 3; x < tileCountX - 3; x++) {
                if (x < cx - 2 || x > cx + 2) {
                    obs.push({ x, y: cy });
                }
            }
            
            // 纵向障碍
            for (let y = 3; y < tileCountY - 3; y++) {
                if (y < cy - 2 || y > cy + 2) {
                    obs.push({ x: cx, y });
                }
            }
            
            return obs;
        }
    },
    // ... 其他地图
];
```

#### 地图加载

```javascript
function loadPresetMap() {
    // 随机选择地图
    const mapIndex = Math.floor(Math.random() * presetMaps.length);
    const map = presetMaps[mapIndex];
    
    // 生成障碍物
    obstacles = map.getObstacles(tileCountX, tileCountY);
    
    console.log(`加载地图: ${map.name}`);
}
```

### 4.2 动态形状化障碍

#### 形状定义

```javascript
const obstacleShapes = [
    { name: "3x3方块", width: 3, height: 3 },
    { name: "2x2角落", width: 2, height: 2 },
    { name: "3x6横条", width: 6, height: 3 },
    { name: "6x3竖条", width: 3, height: 6 },
    { name: "十字形", width: 3, height: 3, pattern: "cross" },
    { name: "L形", width: 3, height: 3, pattern: "L" }
];
```

#### 形状位置计算

```javascript
function getShapePositions(x, y, shape) {
    const positions = [];
    
    if (shape.pattern === 'cross') {
        // 十字形：中心 + 四方向
        const cx = x + 1;
        const cy = y + 1;
        positions.push({ x: cx, y: cy });      // 中心
        positions.push({ x: cx - 1, y: cy });  // 左
        positions.push({ x: cx + 1, y: cy });  // 右
        positions.push({ x: cx, y: cy - 1 });  // 上
        positions.push({ x: cx, y: cy + 1 });  // 下
    } else if (shape.pattern === 'L') {
        // L形
        for (let i = 0; i < 3; i++) {
            positions.push({ x: x, y: y + i }); // 竖线
        }
        positions.push({ x: x + 1, y: y + 2 }); // 横线延伸
        positions.push({ x: x + 2, y: y + 2 });
    } else {
        // 矩形
        for (let dx = 0; dx < shape.width; dx++) {
            for (let dy = 0; dy < shape.height; dy++) {
                positions.push({ x: x + dx, y: y + dy });
            }
        }
    }
    
    return positions;
}
```

#### 预警系统

```javascript
function showShapeWarning(pending) {
    const { shape, x, y } = pending;
    
    // 计算预览框尺寸
    let width, height;
    if (shape.pattern === 'cross' || shape.pattern === 'L') {
        width = height = 3 * gridSize;
    } else {
        width = shape.width * gridSize;
        height = shape.height * gridSize;
    }
    
    // 显示预览框
    warningShapePreview.style.left = (x * gridSize) + 'px';
    warningShapePreview.style.top = (y * gridSize) + 'px';
    warningShapePreview.style.width = width + 'px';
    warningShapePreview.style.height = height + 'px';
    warningShapePreview.style.display = 'block';
    
    // 显示文字提示
    warningText.textContent = `⚠️ ${shape.name}即将出现!`;
    warningText.style.display = 'block';
}
```

### 4.3 颜色主题系统

```javascript
// HSL色彩生成
function getRandomColor() {
    const hue = Math.floor(Math.random() * 360);
    return `hsl(${hue}, 70%, 50%)`;
}

// 应用颜色
function randomizeColors() {
    snakeColor = getRandomColor();
    foodColor = getRandomColor();
    
    // 更新预览
    snakeColorBox.style.background = snakeColor;
    foodColorBox.style.background = foodColor;
    
    // 如果游戏未运行，重绘
    if (!gameRunning) {
        draw();
    }
}
```

---

## 问题与解决方案

### 5.1 蛇快速反向问题

| 项目 | 内容 |
|-----|------|
| **问题描述** | 快速连续按上下或左右键，蛇可能反向撞到自己 |
| **根本原因** | 键盘事件处理与游戏更新不同步 |
| **解决方案** | 使用`nextVelocity`缓冲，确保每帧只处理一个方向变化 |

```javascript
// 按键时只更新缓冲
nextVelocity = { x: 0, y: -1 };

// 更新时才应用
velocity = { x: nextVelocity.x, y: nextVelocity.y };
```

### 5.2 食物生成位置冲突

| 项目 | 内容 |
|-----|------|
| **问题描述** | 随机生成食物可能出现在蛇身或障碍物上 |
| **根本原因** | 纯随机生成，未检查位置有效性 |
| **解决方案** | 使用do-while循环，不断生成直到找到空位 |

### 5.3 动态障碍与蛇重叠

| 项目 | 内容 |
|-----|------|
| **问题描述** | 动态生成的障碍可能直接生成在蛇身上 |
| **解决方案** | 生成前检查所有位置，确保不与蛇身重叠 |

```javascript
function isValidShapePosition(x, y, shape) {
    const positions = getShapePositions(x, y, shape);
    
    for (const pos of positions) {
        if (isSnakeAt(pos.x, pos.y)) return false;
        if (isObstacleAt(pos.x, pos.y)) return false;
    }
    return true;
}
```

### 5.4 地图尺寸适配

| 项目 | 内容 |
|-----|------|
| **问题描述** | 不同地图大小需要动态调整画布尺寸 |
| **解决方案** | 根据选择动态设置canvas尺寸和网格数量 |

```javascript
const mapSizes = {
    small:  { tileCount: 20, canvasSize: 400 },
    medium: { tileCount: 30, canvasSize: 600 },
    large:  { tileCount: 40, canvasSize: 800 }
};

function setMapSize(size) {
    const config = mapSizes[size];
    canvas.width = config.canvasSize;
    canvas.height = config.canvasSize;
    tileCountX = tileCountY = config.tileCount;
}
```

### 5.5 代码文件截断

| 项目 | 内容 |
|-----|------|
| **问题描述** | 写入大文件时被截断，导致JavaScript不完整 |
| **解决方案** | 使用更简洁的代码风格，避免过长的模板字符串 |

---

## 项目结构

```
snake.html
├── HTML 结构
│   ├── 游戏画布 (canvas#gameCanvas)
│   ├── 开始菜单 (.start-menu)
│   ├── 游戏结束界面 (.game-over)
│   ├── 预警提示 (.warning-text, .warning-shape-preview)
│   └── 设置面板 (.settings-panel)
│
├── CSS 样式
│   ├── 布局样式 (flex布局，响应式)
│   ├── 组件样式 (按钮、面板、文字)
│   ├── 动画效果 (blink, pulse-border)
│   └── 主题颜色 (CSS变量)
│
└── JavaScript 逻辑
    ├── 配置常量
    │   ├── difficulties (难度配置)
    │   ├── mapSizes (地图尺寸)
    │   ├── presetMaps (预设地图)
    │   └── obstacleShapes (障碍形状)
    │
    ├── 状态变量
    │   ├── gameRunning, gamePaused
    │   ├── snake (蛇身数组)
    │   ├── food (食物位置)
    │   └── obstacles (障碍物数组)
    │
    ├── 核心函数
    │   ├── initGame() (初始化)
    │   ├── update() (更新状态)
    │   ├── draw() (渲染画面)
    │   └── gameLoop() (游戏循环)
    │
    ├── 功能函数
    │   ├── generateFood() (生成食物)
    │   ├── checkCollisions() (碰撞检测)
    │   ├── loadPresetMap() (加载地图)
    │   └── showShapeWarning() (预警显示)
    │
    └── 事件处理
        ├── 键盘控制 (keydown)
        └── 按钮点击 (onclick)
```

---

## 代码参考

### 完整的游戏循环

```javascript
function gameLoop() {
    if (!gamePaused) {
        update();
    }
    draw();
}

function update() {
    // 应用速度
    velocity = { ...nextVelocity };
    
    if (velocity.x === 0 && velocity.y === 0) return;
    
    // 计算新头部
    const head = {
        x: snake[0].x + velocity.x,
        y: snake[0].y + velocity.y
    };
    
    // 碰撞检测
    if (checkCollisions(head)) return;
    
    // 移动蛇
    snake.unshift(head);
    
    // 吃食物检测
    if (food && head.x === food.x && head.y === food.y) {
        addScore();
        food = generateFood();
    } else {
        snake.pop();
    }
}
```

### 完整的渲染函数

```javascript
function draw() {
    // 清空画布
    ctx.fillStyle = '#0a0a0a';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // 绘制网格
    drawGrid();
    
    // 绘制障碍物
    obstacles.forEach(obs => drawObstacle(obs.x, obs.y, '#7f8c8d'));
    tempObstacles.forEach(obs => drawObstacle(obs.x, obs.y, '#e67e22'));
    
    // 绘制蛇
    drawSnake();
    
    // 绘制食物
    drawFood();
    
    // 暂停提示
    if (gamePaused) drawPauseScreen();
}
```

---

## 总结

本贪吃蛇游戏采用经典的面向过程编程方式，具有以下特点：

1. **架构清晰**：游戏循环、状态管理、渲染分离
2. **扩展性强**：易于添加新地图、新形状、新功能
3. **性能优化**：使用Canvas原生API，避免不必要的重绘
4. **用户体验**：预警系统、暂停功能、多种难度选择
5. **代码组织**：单文件架构，便于部署和维护

通过这个项目，可以学习到游戏开发的核心概念：游戏循环、碰撞检测、状态管理、用户输入处理等。
