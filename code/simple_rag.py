from __future__ import annotations

import math
import os
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import requests


TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_\u4e00-\u9fff]+")
TEXT_EXTENSIONS = {".md", ".txt", ".py", ".html", ".htm"}


@dataclass
class DocumentChunk:
    source: str
    chunk_id: int
    content: str


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_PATTERN.findall(text)]


def iter_text_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in TEXT_EXTENSIONS:
            yield path


def load_chunks(
    root: str | Path,
    chunk_size: int = 500,
    chunk_overlap: int = 100,
) -> list[DocumentChunk]:
    root_path = Path(root)
    if not root_path.exists():
        raise FileNotFoundError(f"Knowledge path not found: {root_path}")

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size.")

    chunks: list[DocumentChunk] = []
    step = chunk_size - chunk_overlap

    for file_path in iter_text_files(root_path):
        try:
            text = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = file_path.read_text(encoding="utf-8", errors="ignore")

        normalized = text.strip()
        if not normalized:
            continue

        for index, start in enumerate(range(0, len(normalized), step)):
            content = normalized[start : start + chunk_size].strip()
            if content:
                chunks.append(
                    DocumentChunk(
                        source=str(file_path.relative_to(root_path)),
                        chunk_id=index,
                        content=content,
                    )
                )

    if not chunks:
        raise ValueError(f"No supported text files found in: {root_path}")

    return chunks


class SimpleRetriever:
    """A tiny TF-IDF retriever suitable for learning/demo projects."""

    def __init__(self, chunks: list[DocumentChunk]) -> None:
        self.chunks = chunks
        self.chunk_tokens = [tokenize(chunk.content) for chunk in chunks]
        self.doc_freq: Counter[str] = Counter()
        self.term_freqs: list[Counter[str]] = []

        for tokens in self.chunk_tokens:
            term_counter = Counter(tokens)
            self.term_freqs.append(term_counter)
            self.doc_freq.update(term_counter.keys())

        self.total_docs = len(chunks)

    def search(self, query: str, top_k: int = 3) -> list[tuple[float, DocumentChunk]]:
        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        query_counter = Counter(query_tokens)
        results: list[tuple[float, DocumentChunk]] = []

        for chunk, term_counter, tokens in zip(
            self.chunks,
            self.term_freqs,
            self.chunk_tokens,
        ):
            if not tokens:
                continue

            score = 0.0
            length_norm = math.sqrt(len(tokens))

            for token, query_weight in query_counter.items():
                if token not in term_counter:
                    continue

                tf = term_counter[token] / length_norm
                idf = math.log((self.total_docs + 1) / (self.doc_freq[token] + 1)) + 1.0
                score += query_weight * tf * idf

            if score > 0:
                results.append((score, chunk))

        results.sort(key=lambda item: item[0], reverse=True)
        return results[:top_k]


@dataclass
class LLMConfig:
    provider: str = "ollama"
    model: str = "qwen3.5:latest"
    api_key: str | None = None
    base_url: str | None = None
    timeout: int = 120
    system_prompt: str = (
        "You are a helpful RAG assistant. Answer only from the provided context. "
        "If the context is insufficient, say so clearly."
    )


class LLMClient:
    def __init__(self, config: LLMConfig) -> None:
        self.config = config

    def answer(self, question: str, context: str) -> str:
        prompt = (
            "Answer the question based only on the context below.\n"
            "If the context is not enough, say: I cannot determine that from the provided context.\n\n"
            f"Context:\n{context}\n\n"
            f"Question:\n{question}"
        )

        if self.config.provider.lower() == "ollama":
            return self._chat_ollama(prompt)
        if self.config.provider.lower() == "openai":
            return self._chat_openai(prompt)
        raise ValueError("provider must be 'ollama' or 'openai'.")

    def _chat_ollama(self, prompt: str) -> str:
        base_url = self.config.base_url or "http://127.0.0.1:11434"
        response = requests.post(
            f"{base_url.rstrip('/')}/api/chat",
            json={
                "model": self.config.model,
                "stream": False,
                "messages": [
                    {"role": "system", "content": self.config.system_prompt},
                    {"role": "user", "content": prompt},
                ],
            },
            timeout=self.config.timeout,
        )
        response.raise_for_status()
        data = response.json()
        return data["message"]["content"]

    def _chat_openai(self, prompt: str) -> str:
        api_key = self.config.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Please set OPENAI_API_KEY or pass api_key.")

        base_url = self.config.base_url or "https://api.openai.com/v1"
        response = requests.post(
            f"{base_url.rstrip('/')}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.config.model,
                "temperature": 0.2,
                "messages": [
                    {"role": "system", "content": self.config.system_prompt},
                    {"role": "user", "content": prompt},
                ],
            },
            timeout=self.config.timeout,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


class SimpleRAG:
    def __init__(
        self,
        knowledge_dir: str | Path,
        llm_config: LLMConfig,
        chunk_size: int = 500,
        chunk_overlap: int = 100,
    ) -> None:
        self.knowledge_dir = Path(knowledge_dir)
        self.chunks = load_chunks(self.knowledge_dir, chunk_size, chunk_overlap)
        self.retriever = SimpleRetriever(self.chunks)
        self.llm = LLMClient(llm_config)

    def ask(self, question: str, top_k: int = 3) -> dict[str, object]:
        results = self.retriever.search(question, top_k=top_k)
        if not results:
            return {
                "answer": "No relevant context was retrieved, so I cannot answer from the knowledge base.",
                "sources": [],
            }

        context_blocks = []
        sources = []
        for score, chunk in results:
            context_blocks.append(
                f"[Source: {chunk.source}#{chunk.chunk_id} | score={score:.3f}]\n{chunk.content}"
            )
            sources.append(
                {
                    "source": chunk.source,
                    "chunk_id": chunk.chunk_id,
                    "score": round(score, 3),
                }
            )

        context = "\n\n".join(context_blocks)
        answer = self.llm.answer(question, context)
        return {"answer": answer, "sources": sources}


def build_demo_rag(provider: str = "ollama") -> SimpleRAG:
    if provider == "openai":
        llm_config = LLMConfig(
            provider="openai",
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            base_url=os.getenv("OPENAI_BASE_URL"),
        )
    else:
        llm_config = LLMConfig(
            provider="ollama",
            model=os.getenv("OLLAMA_MODEL", "qwen3.5:latest"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
        )

    project_root = Path(__file__).resolve().parents[1]
    return SimpleRAG(
        knowledge_dir=project_root,
        llm_config=llm_config,
        chunk_size=500,
        chunk_overlap=100,
    )


if __name__ == "__main__":
    provider = input("Provider (ollama/openai, default ollama): ").strip().lower() or "ollama"
    rag = build_demo_rag(provider)

    print(f"Knowledge dir: {rag.knowledge_dir}")
    print(f"Indexed chunks: {len(rag.chunks)}")
    print("Type your question. Enter q to quit.")

    while True:
        question = input("\nQuestion: ").strip()
        if not question:
            continue
        if question.lower() in {"q", "quit", "exit"}:
            break

        try:
            result = rag.ask(question, top_k=3)
        except requests.RequestException as exc:
            print(f"LLM request failed: {exc}")
            continue
        except Exception as exc:
            print(f"Error: {exc}")
            continue

        print("\nAnswer:")
        print(result["answer"])
        print("\nSources:")
        for item in result["sources"]:
            print(f"- {item['source']}#{item['chunk_id']} (score={item['score']})")
