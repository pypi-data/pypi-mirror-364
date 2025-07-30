import difflib
from sentence_transformers import SentenceTransformer, util

class PromptDiff:
    def __init__(self):
        self._model = None
    
    def text_diff(self, old, new):
        lines1 = old.splitlines()
        lines2 = new.splitlines()
        diff = difflib.ndiff(lines1, lines2)
        return "\n".join(diff)
    
    def semantic_diff(self, old, new):
        if self._model is None:
            self._model = SentenceTransformer("all-MiniLM-L6-v2")
        
        embeddings = self._model.encode([old, new])
        similarity = util.cos_sim(embeddings[0], embeddings[1])
        return float(similarity[0][0])

