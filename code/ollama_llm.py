from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

import requests


@dataclass
#默认配置
class OllamaConfig:

    base_url: str = "http://127.0.0.1:11434"
    model: str = "qwen3.5:latest"
    timeout: int = 120
    system_prompt: str = "You are a helpful assistant."
    max_history_turns: int = 20
    max_context_chars: int = 60000
    #传给 Ollama 的模型参数，如 temperature、num_predict 等。
    options: dict[str, Any] = field(default_factory=dict)


class OllamaChatAPI:
    """支持多轮对话和上下文裁剪的 Ollama 客户端。"""

    def __init__(self, config: OllamaConfig | None = None) -> None:
        self.config = config or OllamaConfig()
        self.chat_url = f"{self.config.base_url.rstrip('/')}/api/chat"
        self.tags_url = f"{self.config.base_url.rstrip('/')}/api/tags"
        # 内存中的会话历史，格式与 Ollama chat 接口一致。
        self.history: list[dict[str, str]] = []

    def list_models(self) -> list[str]:
        """读取本地 Ollama 已安装模型列表。"""
        response = requests.get(self.tags_url, timeout=self.config.timeout)
        response.raise_for_status()
        data = response.json()
        return [item["name"] for item in data.get("models", [])]

    def clear_history(self) -> None:
        """清空当前会话历史。"""
        self.history.clear()

    def set_history_limits(
        self,
        max_history_turns: int | None = None,
        max_context_chars: int | None = None,
    ) -> None:
        """动态修改上下文限制，并立即对当前历史做一次裁剪。"""
        if max_history_turns is not None:
            self.config.max_history_turns = max_history_turns
        if max_context_chars is not None:
            self.config.max_context_chars = max_context_chars
        self.history = self._trim_history(self.history)

    def chat(
        self,
        user_message: str,
        history: list[dict[str, str]] | None = None,
        stream: bool = False,
        use_memory: bool = True,
    ) -> str:
        """
        发起一次对话请求。

        参数说明：
        - user_message: 当前用户输入
        - history: 传入外部历史；如果传了，就优先使用它
        - stream: 是否流式输出
        - use_memory: 是否使用并更新对象内部维护的 history
        """
        if history is not None:
            working_history = self._trim_history(history.copy())
        elif use_memory:
            working_history = self._trim_history(self.history.copy())
        else:
            working_history = []

        messages = self._build_messages(working_history, user_message)
        payload = {
            "model": self.config.model,
            "messages": messages,
            "stream": stream,
            "options": self.config.options,
        }

        response = requests.post(
            self.chat_url,
            json=payload,
            timeout=self.config.timeout,
            stream=stream,
        )
        response.raise_for_status()

        if stream:
            assistant_reply = self._read_stream(response)
        else:
            data = response.json()
            assistant_reply = data["message"]["content"]

        # 只有在使用内部记忆，且没有传入外部 history 时，才写回对象状态。
        if use_memory and history is None:
            self.history.append({"role": "user", "content": user_message})
            self.history.append({"role": "assistant", "content": assistant_reply})
            self.history = self._trim_history(self.history)

        return assistant_reply

    def chat_loop(self, stream: bool = False) -> None:
        """命令行多轮对话模式。"""
        print(f"Current model: {self.config.model}")
        print("Enter content to chat. Type /exit to quit, /clear to clear history, /models to list models.")

        while True:
            try:
                user_input = input("\nYou: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nConversation ended.")
                break

            if not user_input:
                continue

            if user_input in {"/exit", "/quit"}:
                print("Conversation ended.")
                break

            if user_input == "/clear":
                self.clear_history()
                print("History cleared.")
                continue

            if user_input == "/models":
                try:
                    print("Local models:", self.list_models())
                except requests.RequestException as exc:
                    print(f"Failed to get models: {exc}")
                continue

            try:
                if stream:
                    print("Assistant: ", end="", flush=True)
                    self.chat(user_input, stream=True, use_memory=True)
                else:
                    reply = self.chat(user_input, stream=False, use_memory=True)
                    print(f"Assistant: {reply}")
            except requests.RequestException as exc:
                print(f"Request failed: {exc}")

    def _build_messages(
        self,
        history: list[dict[str, str]],
        user_message: str,
    ) -> list[dict[str, str]]:
        """拼接 system prompt、历史消息和当前输入。"""
        messages: list[dict[str, str]] = []

        if self.config.system_prompt:
            messages.append({"role": "system", "content": self.config.system_prompt})

        messages.extend(history)
        messages.append({"role": "user", "content": user_message})
        return self._trim_messages_by_chars(messages)

    def _trim_history(self, history: list[dict[str, str]]) -> list[dict[str, str]]:
        """
        对历史进行两层裁剪：
        1. 按轮数裁剪
        2. 按字符预算裁剪
        """
        if self.config.max_history_turns > 0:
            max_messages = self.config.max_history_turns * 2
            history = history[-max_messages:]

        messages = self._trim_messages_by_chars(history)
        return [
            message
            for message in messages
            if message.get("role") in {"user", "assistant"}
        ]

    def _trim_messages_by_chars(
        self,
        messages: list[dict[str, str]],
    ) -> list[dict[str, str]]:
        """
        按字符预算保留最近消息。

        这里不是精确 token 统计，而是字符数近似控制。
        对本地脚本来说足够轻量，也容易理解。
        """
        max_chars = self.config.max_context_chars
        if max_chars <= 0:
            return messages

        system_messages = [m for m in messages if m.get("role") == "system"]
        other_messages = [m for m in messages if m.get("role") != "system"]

        kept: list[dict[str, str]] = []
        total_chars = sum(
            len(message.get("content", "")) + len(message.get("role", ""))
            for message in system_messages
        )

        # 倒序遍历，优先保留最近的上下文。
        for message in reversed(other_messages):
            content = message.get("content", "")
            role = message.get("role", "")
            message_size = len(content) + len(role)

            if total_chars + message_size > max_chars:
                continue

            kept.append(message)
            total_chars += message_size

        kept.reverse()
        return system_messages + kept

    @staticmethod
    def _read_stream(response: requests.Response) -> str:
        """读取 Ollama 的流式响应，并实时打印到终端。"""
        chunks: list[str] = []
        for line in response.iter_lines():
            if not line:
                continue

            item = json.loads(line.decode("utf-8"))
            content = item.get("message", {}).get("content", "")
            if content:
                chunks.append(content)
                print(content, end="", flush=True)

        print()
        return "".join(chunks)


if __name__ == "__main__":
    # 这里是一个最小可运行示例，你可以直接改 model 和参数后运行。
    config = OllamaConfig(
        base_url="http://127.0.0.1:11434",
        model="qwen3.5:latest",
        system_prompt="You are a helpful AI assistant.",
        max_history_turns=5,
        max_context_chars=6000,
        options={
            "temperature": 0.7,
            "num_predict": 512,
        },
    )

    client = OllamaChatAPI(config)

    try:
        print("Local models:", client.list_models())
    except requests.RequestException as exc:
        print(f"Failed to query local models: {exc}")

    client.chat_loop(stream=False)
