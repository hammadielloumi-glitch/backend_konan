
from typing import List, Dict
class BaseAgent:
    domain: str = "general"
    def build_prompt(self, message: str, citations: List[Dict]) -> list:
        sys = {"role": "system", "content": ("Tu es Konan, assistant juridique tunisien. "
                                             "Réponds factuellement, cite les articles trouvés, "
                                             "et indique les limites en cas d'incertitude. "
                                             "Si l'entrée est en arabe, réponds en arabe.")}
        context = {"role": "system", "content": "Contexte: " + "\n".join([f"[{c['metadata'].get('reference','?')}] {c['text']}" for c in citations])}
        user = {"role": "user", "content": message}
        return [sys, context, user]
