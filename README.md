# 11day-class

## 更新：Dify 本地用户系统 MVP

当前仓库已新增 `dify_mvp_app/`，用于演示一个可本地运行的最小化应用：

- 基于 `Flask` 的注册/登录用户系统（密码哈希存储）
- 每个用户独立保存 Dify `conversation_id`，确保会话隔离
- 后端代理调用 Dify Chat API，避免在前端暴露 `DIFY_API_KEY`
- 使用 `SQLite` 持久化用户与聊天消息

运行示例：

```bash
cd dify_mvp_app
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# 配置 DIFY_API_KEY 后启动
python app.py
```

访问：`http://localhost:8080`

## 更新：Simple RAG 示例

当前项目已包含 `code/simple_rag.py`，这是一个轻量级 RAG 示例。

- 会扫描仓库中的 `.md`、`.txt`、`.py`、`.html`、`.htm` 文件。
- 会将文档切分为多个片段（chunk）。
- 会使用轻量级 TF-IDF 检索器召回相关片段。
- 会将召回上下文发送给本地 `Ollama` 模型或 `OpenAI API`。

运行方式：

```bash
python code/simple_rag.py
```

环境变量：

- `OLLAMA_BASE_URL` 与 `OLLAMA_MODEL`（用于 Ollama 模式）
- `OPENAI_API_KEY`、`OPENAI_BASE_URL` 与 `OPENAI_MODEL`（用于 OpenAI 模式）

### 更新：基于gradio和fastapi的简易前后端

- `code/gradio_fastapi_ollama.py`
  - 提供基于 `FastAPI` 的后端接口：
    - `GET /api/health`
    - `GET /api/models`
    - `POST /api/chat`
    - `POST /api/clear`
  - 在 `/gradio` 路径挂载 `Gradio` 对话界面
  - 复用 `OllamaChatAPI` 的会话记忆能力，并支持按会话切换模型
- `code/simple_rag.py`
  - 内置轻量级本地检索器（`TF-IDF` 风格打分）
  - 单脚本支持 `ollama` 与 `openai` 两种提供方
  - 返回可追溯来源信息（`source`、`chunk_id`、`score`）

快速运行：

```bash
# RAG 示例
python code/simple_rag.py

# FastAPI + Gradio 示例
python code/gradio_fastapi_ollama.py
# 然后访问 http://127.0.0.1:8000/gradio
```


## 项目简介

一个用于记录 **11 天编程课程学习过程** 的仓库。

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
├─ dify_mvp_app/            # Dify 用户系统 MVP（Flask + SQLite）
├─ vibetest/                # AI 辅助生成的小项目与文档
├─ certificate/             # 课程相关图片/证明材料
├─ study.md                 # 学习笔记与过程记录
└─ README.md                # 项目说明文档
```

## 内容说明

### Python 代码

`code/` 目录用于保存课程中的练习代码、接口调用示例和阶段性成果。

### Dify MVP 应用

`dify_mvp_app/` 目录包含一个与本地 Dify 联调的最小用户系统实践：

- `app.py`：Flask 主程序（注册、登录、聊天、会话映射）
- `templates/` 与 `static/`：基础页面与样式
- `.env.example`：Dify 与应用配置模板
- `README.md`：该子项目的独立运行说明

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


## 当前学习范围

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
