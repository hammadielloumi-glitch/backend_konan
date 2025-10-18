
from typing import List, Dict
import httpx
from ..core.config import settings
OPENAI_API_BASE = "https://api.openai.com/v1"
async def chat_completion(messages: List[Dict], model: str = "gpt-4o-mini"):
    if not settings.OPENAI_API_KEY:
        return {"role": "assistant", "content": "Clé OpenAI absente. Réponse hors ligne basée sur la recherche locale."}
    headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": messages, "temperature": 0.2}
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(f"{OPENAI_API_BASE}/chat/completions", json=payload, headers=headers)
        r.raise_for_status()
        data = r.json()
        content = data["choices"][0]["message"]["content"]
        return {"role": "assistant", "content": content}
