# Dify MVP App

这是一个最小可运行的示例：
- 用户注册/登录
- 每个用户独立会话（保存 `user_id -> dify_conversation_id`）
- 聊天消息落库（SQLite）
- 后端代理调用 Dify，前端不会暴露 Dify API Key

## 目录

- `app.py` Flask 主程序
- `templates/` 页面模板
- `static/style.css` 基础样式
- `data.sqlite3` 运行后自动生成数据库

## 前置条件

1. 你的本地 Dify 已启动（默认 API 地址 `http://localhost:5001`）
2. 你已在 Dify 控制台创建应用并拿到 API Key（`app-...`）

## 本地运行

```powershell
cd d:\11days\github_res\11day-class\dify_mvp_app
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

编辑 `.env`，至少填写：

```env
SECRET_KEY=replace-with-random-secret
DIFY_BASE_URL=http://localhost:5001
DIFY_API_KEY=app-xxxxxxxxxxxxxxxxxxxxxxxx
```

启动：

```powershell
python app.py
```

访问：`http://localhost:8080`

快速验证：浏览器打开后，先注册新用户，再登录并发送一条消息，确认可返回 Dify 响应。

## Docker 运行

```powershell
cd d:\11days\github_res\11day-class\dify_mvp_app
copy .env.example .env
# 编辑 .env，填入真实 Dify API Key

docker compose up -d --build
```

访问：`http://localhost:8080`

## MVP 设计说明

1. 鉴权：基于会话 cookie（Flask session）
2. 用户系统：`users` 表存储用户名和加密密码
3. 会话隔离：`conversation_state` 表按 `user_id` 记录 Dify 的 `conversation_id`
4. 消息记录：`messages` 表保存用户和 AI 对话
5. 安全边界：仅后端请求 Dify，`DIFY_API_KEY` 不下发前端

## 已知限制（MVP 阶段）

- 未做 CSRF 防护
- 未做限流与审计
- 单应用单会话（每个用户只维护 1 条会话链）

可在下一步扩展：多会话、管理员面板、JWT、RBAC、限流和日志。
