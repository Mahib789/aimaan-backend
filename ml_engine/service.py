import os
import re

import joblib
import numpy as np
from scipy.sparse import hstack

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_DIR = os.environ.get("ML_MODELS_DIR", os.path.join(BASE_DIR, "ml_models"))

MODEL_PATH = os.path.join(MODEL_DIR, "xgb_model.pkl")
WORD_VECTORIZER_PATH = os.path.join(MODEL_DIR, "word_vectorizer.pkl")
CHAR_VECTORIZER_PATH = os.path.join(MODEL_DIR, "char_vectorizer.pkl")
SHAP_PATH = os.path.join(MODEL_DIR, "shap_explainer.pkl")


def _load_joblib(path, label):
    if not os.path.exists(path):
        raise RuntimeError(f"{label} file not found: {path}")
    return joblib.load(path)


model = _load_joblib(MODEL_PATH, "ML model")
word_vectorizer = _load_joblib(WORD_VECTORIZER_PATH, "Word vectorizer")
char_vectorizer = _load_joblib(CHAR_VECTORIZER_PATH, "Character vectorizer")
shap_explainer = _load_joblib(SHAP_PATH, "SHAP explainer")

stopwords = {
    "i", "me", "my", "we", "our", "you", "your", "he", "she", "it", "they", "them",
    "this", "that", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "do", "does", "did", "a", "an", "the", "and", "or", "but", "if", "in", "on", "at",
    "to", "from", "for", "with", "hai", "hain", "ka", "ki", "ke", "ko", "se", "mein", "par", "aur",
}

fraud_keywords = {
    "prize", "winner", "won", "reward", "cash", "money", "free", "claim", "urgent", "urgently",
    "verify", "verification", "suspended", "bisp", "draw", "lottery", "call", "account", "otp",
    "login", "password", "click", "link", "gift", "offer", "biometric", "sim", "block", "blocked",
    "freeze", "frozen", "debit", "credit", "bank", "hbl", "jazzcash", "easypaisa",
}


def normalize(text):
    text = str(text or "").lower()
    text = re.sub(r"http\S+|www\S+", " urltoken ", text)
    text = re.sub(r"\b03\d{9}\b", " phonetoken ", text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def preprocess(text):
    clean = normalize(text)
    return " ".join(t for t in clean.split() if t not in stopwords and len(t) > 2)


def build_features(text):
    clean_text = preprocess(text)
    word_vec = word_vectorizer.transform([clean_text])
    char_vec = char_vectorizer.transform([clean_text])
    return hstack([word_vec, char_vec]), clean_text


def get_shap_explanation(X, clean_text):
    try:
        dense = X.toarray().astype(np.float32)
        shap_values = shap_explainer.shap_values(dense)
        values = shap_values[1][0] if isinstance(shap_values, list) else shap_values[0]
        values = np.abs(values)

        word_features = word_vectorizer.get_feature_names_out()
        input_words = set(clean_text.split())
        important = []

        for i, word in enumerate(word_features):
            if i >= len(values):
                break
            word = word.lower()
            score = float(values[i])
            if word in input_words and score > 0.001:
                important.append({"feature": word, "impact": round(score, 4), "source": "shap"})

        for word in input_words:
            if word in fraud_keywords and not any(x["feature"] == word for x in important):
                important.append({"feature": word, "impact": 0.95, "source": "rule"})

        if not important:
            important = [
                {"feature": word, "impact": 0.15, "source": "fallback"}
                for word in list(input_words)[:10]
            ]

        return sorted(important, key=lambda x: x["impact"], reverse=True)[:10]
    except Exception:
        return [
            {"feature": word, "impact": 0.1, "source": "fallback"}
            for word in clean_text.split()[:10]
        ]


def generate_reasons(features):
    words = {f["feature"] for f in features}
    reasons = []

    if words & {"urgent", "urgently", "verify", "verification", "suspended", "block", "blocked"}:
        reasons.append("Uses urgency-based manipulation")
    if words & {"prize", "winner", "won", "cash", "free", "reward"}:
        reasons.append("Contains reward-based scam pattern")
    if words & {"bank", "otp", "password", "account", "login", "hbl", "jazzcash", "easypaisa"}:
        reasons.append("Targets sensitive information or financial accounts")
    if words & {"click", "call", "link", "claim"}:
        reasons.append("Encourages suspicious user action")

    return reasons or ["Detected using ML phishing pattern analysis"]


def rule_override(clean_text, safe_prob, fraud_prob):
    words = set(clean_text.split())
    strong = words & fraud_keywords
    if len(strong) >= 2:
        fraud_prob = max(fraud_prob, 0.85)
        safe_prob = min(safe_prob, 1 - fraud_prob)
    return safe_prob, fraud_prob


def predict_message(text):
    X, clean_text = build_features(text)

    if not clean_text or X.nnz < 2:
        return {
            "text": clean_text,
            "label": "SAFE",
            "safe": 0.95,
            "fraud": 0.05,
            "xai_method": "HYBRID_SHAP_RULE_FALLBACK",
            "important_features": [],
            "reasons": ["Not enough meaningful content detected"],
        }

    probs = model.predict_proba(X)[0]
    safe_prob = float(probs[0])
    fraud_prob = float(probs[1])
    safe_prob, fraud_prob = rule_override(clean_text, safe_prob, fraud_prob)

    label = "FRAUD" if fraud_prob >= float(os.environ.get("FRAUD_THRESHOLD", "0.40")) else "SAFE"
    important_features = get_shap_explanation(X, clean_text)

    return {
        "text": clean_text,
        "label": label,
        "safe": round(safe_prob, 4),
        "fraud": round(fraud_prob, 4),
        "xai_method": "HYBRID_SHAP_RULE_FALLBACK",
        "important_features": important_features,
        "reasons": generate_reasons(important_features),
    }
