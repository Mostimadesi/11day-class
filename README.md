# 11day-class

> 一个用于记录 **11 天编程课程学习过程** 的仓库。

这个项目主要用来沉淀学习过程中的代码练习、案例脚本、实验记录和学习笔记。  
仓库会随着课程推进持续更新，既保存阶段性成果，也方便后续回顾与复盘。

## 项目目标

希望通过这 11 天的连续学习，逐步完成从基础语法到实际调用大模型接口的积累：

- **每天都有可见的学习产出**
- **每天都保留简洁的过程记录**
- **用代码和文字同步沉淀学习成果**

## 仓库结构

```text
11day-class/
├─ code/                    # Python 练习代码与示例脚本
│  ├─ hello_world.py
│  ├─ simple_calcu.py
│  ├─ deepseek_langchain_example.py
│  └─ ollama_llm.py
├─ vibetest/                # AI 辅助生成的小项目与文档
├─ certificate/             # 课程相关图片/证明材料
├─ study.md                 # 学习笔记与过程记录
└─ README.md                # 项目说明文档
```

## 内容说明

### Python 代码

`code/` 目录用于保存课程中的练习代码、接口调用示例和阶段性成果。

#### `hello_world.py`

课程中的基础练习，包含几个入门函数示例：

- 输出 `Hello, World!`
- 通过 `input()` 接收用户输入并拼接句子
- 使用 `try...except` 处理异常输入
- 使用条件判断输出不同语言的问候语
- 使用循环实现列表最大值查找

#### `simple_calcu.py`

一个简单的命令行计算器小项目：

- 支持 `+`、`-`、`*`、`/`、`%` 运算
- 支持命令行连续输入表达式
- 输入 `q` 可退出程序
- 包含基础的输入格式校验与异常处理

#### `deepseek_langchain_example.py`

一个基于 **LangChain + DeepSeek API** 的最小调用示例：

- 从环境变量读取 `DEEPSEEK_API_KEY`
- 使用 `ChatOpenAI` 兼容接口调用 DeepSeek 模型
- 支持自定义 `model` 和 `base_url`
- 适合作为 API 调用和 LangChain 入门参考

#### `ollama_llm.py`

一个较完整的 **Ollama 本地对话客户端示例**：

- 使用 `requests` 调用本地 Ollama 接口
- 支持查看本地已安装模型
- 支持多轮对话与历史记录维护
- 支持上下文裁剪，避免历史消息过长
- 支持流式与非流式输出
- 支持通过配置类统一管理 `model`、`timeout`、`system_prompt` 等参数

### Markdown 学习文档

仓库中的 `.md` 文件主要用于整理学习过程中的文字内容，例如：

- **每日学习笔记**
- **重点知识总结**
- **问题排查与报错记录**
- **学习心得与阶段复盘**

其中：

- `study.md`：记录课程学习内容、环境配置过程、概念总结和阶段实践

### 其他内容

- `vibetest/`：AI 辅助生成的小项目实验内容，例如贪吃蛇网页小游戏及说明文档
- `certificate/`：课程相关图片或阶段性成果材料

## 运行方式

建议在项目根目录下使用 Python 运行示例脚本：

```bash
python code/hello_world.py
python code/simple_calcu.py
python code/deepseek_langchain_example.py
python code/ollama_llm.py
```

### 运行说明

- 运行 `deepseek_langchain_example.py` 前，需要先配置环境变量 `DEEPSEEK_API_KEY`
- 运行 `ollama_llm.py` 前，需要先在本地安装并启动 **Ollama**
- 若涉及第三方库，请先安装对应依赖，例如 `requests`、`langchain-openai`、`langchain-core`

## 当前学习范围

从目前的仓库内容来看，已经覆盖了以下主题：

- Python 基础语法与函数练习
- 条件判断、循环与异常处理
- 命令行交互程序编写
- API Key 与模型调用基础配置
- LangChain 调用大模型
- Ollama 本地模型部署与多轮对话实践
- AI 辅助生成小项目并进行反向学习

## 结语

这个仓库不仅是课程作业的存放地，也是一次完整学习过程的记录。

希望在课程结束时，这里能够留下：

- **清晰的代码成果**
- **完整的学习笔记**
- **真实的成长轨迹**
