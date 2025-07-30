from typing import List, Tuple, Optional

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    _has_transformers = True
except ImportError:
    _has_transformers = False

class VectorMemory:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.data: List[Tuple[str, any]] = []
        if _has_transformers:
            self.model = SentenceTransformer(model_name)
        else:
            self.model = None

    def add(self, text: str, meta: any = None):
        self.data.append((text, meta))

    def search(self, query: str, top_k: int = 3) -> List[Tuple[str, any, float]]:
        if not _has_transformers or not self.model:
            # Fallback: return most recent
            return [(t, m, 1.0) for t, m in self.data[-top_k:]]
        texts = [t for t, _ in self.data]
        if not texts:
            return []
        q_emb = self.model.encode([query])[0]
        d_embs = self.model.encode(texts)
        sims = np.dot(d_embs, q_emb) / (np.linalg.norm(d_embs, axis=1) * np.linalg.norm(q_emb) + 1e-8)
        ranked = sorted(zip(texts, [m for _, m in self.data], sims), key=lambda x: -x[2])
        return ranked[:top_k]

    def clear(self):
        self.data.clear() 