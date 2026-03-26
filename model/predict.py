import os
import pickle

_MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")
_pipeline = None
_categories = None

def _load():
    global _pipeline, _categories
    if _pipeline is None:
        with open(_MODEL_PATH, "rb") as f:
            data = pickle.load(f)
        _pipeline = data["pipeline"]
        _categories = data["categories"]

def predict(text: str) -> dict:
    _load()
    proba = _pipeline.predict_proba([text])[0]
    scores = {cat: round(float(p) * 100, 1) for cat, p in zip(_categories, proba)}
    label = max(scores, key=scores.get)
    confidence = scores[label]
    return {"category": label, "confidence": confidence, "scores": scores}