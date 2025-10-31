import os, httpx

BASE = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434")

async def chat(model: str, messages: list[dict], temperature: float = 0.2, stream: bool = False) -> str:
    """
    Use the legacy Ollama endpoint (/api/chat) exclusively, since your server
    responds correctly there (per your curl test). This avoids 404s from /v1/*.
    """
    async with httpx.AsyncClient(timeout=120) as client:
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        }
        r = await client.post(f"{BASE}/api/chat", json=payload)
        r.raise_for_status()
        data = r.json()
        # Primary schema: {"message": {"content": "..."}}
        msg = data.get("message") or {}
        content = (msg.get("content") or "").strip()
        if not content and "choices" in data:
            # Some variants may still return OpenAI-like `choices`
            content = data["choices"][0]["message"]["content"].strip()
        return content