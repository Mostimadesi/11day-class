from __future__ import annotations

import uuid
from dataclasses import replace
from typing import Any

import gradio as gr
import requests
import uvicorn
from fastapi import FastAPI, HTTPException
from gradio.routes import mount_gradio_app
from pydantic import BaseModel, Field

from ollama_llm import OllamaChatAPI, OllamaConfig


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: str | None = None
    model: str | None = None


class ChatResponse(BaseModel):
    session_id: str
    reply: str


class ClearRequest(BaseModel):
    session_id: str


class OllamaService:
    """Manage chat sessions and route requests to Ollama client instances."""

    def __init__(self, base_config: OllamaConfig | None = None) -> None:
        self.base_config = base_config or OllamaConfig()
        self.sessions: dict[str, OllamaChatAPI] = {}

    def _new_client(self, model: str | None = None) -> OllamaChatAPI:
        config = replace(self.base_config)
        # Ensure options dict is not shared across sessions.
        config.options = dict(self.base_config.options)
        if model:
            config.model = model
        return OllamaChatAPI(config)

    def get_client(self, session_id: str, model: str | None = None) -> OllamaChatAPI:
        if session_id not in self.sessions:
            self.sessions[session_id] = self._new_client(model=model)
            return self.sessions[session_id]

        client = self.sessions[session_id]
        if model and model != client.config.model:
            # Switch model for this session while preserving limits/options.
            current_cfg = client.config
            new_cfg = replace(current_cfg)
            new_cfg.options = dict(current_cfg.options)
            new_cfg.model = model
            new_client = OllamaChatAPI(new_cfg)
            new_client.history = client.history.copy()
            self.sessions[session_id] = new_client
            return new_client

        return client

    def chat(self, message: str, session_id: str | None = None, model: str | None = None) -> ChatResponse:
        sid = session_id or str(uuid.uuid4())
        client = self.get_client(sid, model=model)
        try:
            reply = client.chat(message, stream=False, use_memory=True)
        except requests.RequestException as exc:
            raise HTTPException(status_code=502, detail=f"Ollama request failed: {exc}") from exc
        return ChatResponse(session_id=sid, reply=reply)

    def clear(self, session_id: str) -> dict[str, Any]:
        if session_id in self.sessions:
            self.sessions[session_id].clear_history()
        return {"ok": True, "session_id": session_id}

    def list_models(self) -> list[str]:
        temp_client = OllamaChatAPI(self.base_config)
        try:
            return temp_client.list_models()
        except requests.RequestException as exc:
            raise HTTPException(status_code=502, detail=f"Failed to list models: {exc}") from exc


service = OllamaService(
    OllamaConfig(
        base_url="http://127.0.0.1:11434",
        model="qwen3.5:latest",
        system_prompt="You are a helpful AI assistant.",
        max_history_turns=5,
        max_context_chars=6000,
        options={"temperature": 0.7, "num_predict": 512},
    )
)

app = FastAPI(title="Ollama Chat API", version="0.1.0")


@app.get("/api/health")
def health() -> dict[str, bool]:
    return {"ok": True}


@app.get("/api/models")
def models() -> dict[str, list[str]]:
    return {"models": service.list_models()}


@app.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    return service.chat(payload.message, payload.session_id, payload.model)


@app.post("/api/clear")
def clear(payload: ClearRequest) -> dict[str, Any]:
    return service.clear(payload.session_id)


def build_gradio_ui() -> gr.Blocks:
    with gr.Blocks(title="Ollama Chat") as demo:
        gr.Markdown("## Ollama Chat (Gradio + FastAPI)")
        session_state = gr.State(value="")

        with gr.Row():
            model_box = gr.Textbox(value=service.base_config.model, label="Model")
            session_box = gr.Textbox(label="Session ID (auto-generated)", interactive=False)

        chatbot = gr.Chatbot(height=480)
        msg = gr.Textbox(label="Message", placeholder="Type your message and press Enter")

        with gr.Row():
            send_btn = gr.Button("Send", variant="primary")
            clear_btn = gr.Button("Clear")

        def ui_chat(
            user_message: str,
            chat_history: list[dict[str, str]],
            sid: str,
            model: str,
        ):
            history = list(chat_history or [])
            try:
                result = service.chat(user_message, sid or None, model or None)
                history.append({"role": "user", "content": user_message})
                history.append({"role": "assistant", "content": result.reply})
                return "", history, result.session_id, result.session_id
            except HTTPException as exc:
                history.append({"role": "user", "content": user_message})
                history.append(
                    {
                        "role": "assistant",
                        "content": f"[Error {exc.status_code}] {exc.detail}",
                    }
                )
                return "", history, sid, sid
            except Exception as exc:
                history.append({"role": "user", "content": user_message})
                history.append(
                    {"role": "assistant", "content": f"[Unexpected Error] {exc}"}
                )
                return "", history, sid, sid

        def ui_clear(sid: str):
            if sid:
                service.clear(sid)
            return [], sid

        send_btn.click(
            ui_chat,
            inputs=[msg, chatbot, session_state, model_box],
            outputs=[msg, chatbot, session_state, session_box],
        )
        msg.submit(
            ui_chat,
            inputs=[msg, chatbot, session_state, model_box],
            outputs=[msg, chatbot, session_state, session_box],
        )
        clear_btn.click(ui_clear, inputs=[session_state], outputs=[chatbot, session_box])

    return demo


gradio_app = build_gradio_ui()
app = mount_gradio_app(app, gradio_app, path="/gradio")


if __name__ == "__main__":
    uvicorn.run("gradio_fastapi_ollama:app", host="0.0.0.0", port=8000, reload=True)
