import os
import sqlite3
from datetime import datetime, timezone
from functools import wraps

import requests
from dotenv import load_dotenv
from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data.sqlite3")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-only-secret")
app.config["DIFY_BASE_URL"] = os.getenv("DIFY_BASE_URL", "http://localhost:5001")
app.config["DIFY_API_KEY"] = os.getenv("DIFY_API_KEY", "")
app.config["REQUEST_TIMEOUT"] = int(os.getenv("DIFY_TIMEOUT_SECONDS", "60"))


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS conversation_state (
    user_id INTEGER PRIMARY KEY,
    dify_conversation_id TEXT,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
"""


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        g.db = conn
    return g.db


@app.teardown_appcontext
def close_db(_error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    db = sqlite3.connect(DB_PATH)
    db.executescript(SCHEMA)
    db.commit()
    db.close()


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login"))
        return func(*args, **kwargs)

    return wrapper


def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    db = get_db()
    return db.execute("SELECT id, username FROM users WHERE id = ?", (user_id,)).fetchone()


@app.route("/")
def home():
    if session.get("user_id"):
        return redirect(url_for("chat"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if len(username) < 3:
            flash("用户名至少 3 个字符")
            return render_template("register.html")
        if len(password) < 6:
            flash("密码至少 6 个字符")
            return render_template("register.html")

        db = get_db()
        exists = db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
        if exists:
            flash("用户名已存在")
            return render_template("register.html")

        db.execute(
            "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
            (username, generate_password_hash(password), now_iso()),
        )
        db.commit()
        flash("注册成功，请登录")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        db = get_db()
        user = db.execute(
            "SELECT id, username, password_hash FROM users WHERE username = ?", (username,)
        ).fetchone()

        if not user or not check_password_hash(user["password_hash"], password):
            flash("用户名或密码错误")
            return render_template("login.html")

        session.clear()
        session["user_id"] = user["id"]
        return redirect(url_for("chat"))

    return render_template("login.html")


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/chat", methods=["GET", "POST"])
@login_required
def chat():
    user = current_user()
    if request.method == "POST":
        message = request.form.get("message", "").strip()
        if not message:
            flash("消息不能为空")
            return redirect(url_for("chat"))

        try:
            reply = call_dify(user["id"], message)
            flash(f"AI: {reply}", "answer")
        except RuntimeError as exc:
            flash(str(exc))

        return redirect(url_for("chat"))

    db = get_db()
    messages = db.execute(
        "SELECT role, content, created_at FROM messages WHERE user_id = ? ORDER BY id ASC",
        (user["id"],),
    ).fetchall()
    return render_template("chat.html", user=user, messages=messages)


def call_dify(user_id: int, message: str) -> str:
    if not app.config["DIFY_API_KEY"]:
        raise RuntimeError("未配置 DIFY_API_KEY，请先填写 .env")

    db = get_db()
    state = db.execute(
        "SELECT dify_conversation_id FROM conversation_state WHERE user_id = ?", (user_id,)
    ).fetchone()
    conversation_id = state["dify_conversation_id"] if state else ""

    payload = {
        "inputs": {},
        "query": message,
        "response_mode": "blocking",
        "conversation_id": conversation_id,
        "user": f"user-{user_id}",
    }

    try:
        response = requests.post(
            f"{app.config['DIFY_BASE_URL'].rstrip('/')}/v1/chat-messages",
            headers={
                "Authorization": f"Bearer {app.config['DIFY_API_KEY']}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=app.config["REQUEST_TIMEOUT"],
        )
    except requests.RequestException as exc:
        raise RuntimeError(f"请求 Dify 失败: {exc}") from exc

    if response.status_code >= 400:
        raise RuntimeError(f"Dify 返回错误 {response.status_code}: {response.text}")

    data = response.json()
    answer = data.get("answer", "").strip()
    new_conversation_id = data.get("conversation_id", conversation_id)

    db.execute(
        "INSERT INTO messages (user_id, role, content, created_at) VALUES (?, ?, ?, ?)",
        (user_id, "user", message, now_iso()),
    )
    db.execute(
        "INSERT INTO messages (user_id, role, content, created_at) VALUES (?, ?, ?, ?)",
        (user_id, "assistant", answer or "(空响应)", now_iso()),
    )
    db.execute(
        "INSERT INTO conversation_state (user_id, dify_conversation_id, updated_at) VALUES (?, ?, ?)\n"
        "ON CONFLICT(user_id) DO UPDATE SET dify_conversation_id = excluded.dify_conversation_id, updated_at = excluded.updated_at",
        (user_id, new_conversation_id, now_iso()),
    )
    db.commit()

    return answer or "(Dify 未返回文本)"


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8080, debug=True)
