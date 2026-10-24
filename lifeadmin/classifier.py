"""Document type classifier.

Default: transparent keyword scoring (no ML needed, works offline).
Optional: `train_ml_classifier()` builds a scikit-learn Naive Bayes model from
your own labelled documents once you have enough data.
"""
from __future__ import annotations

import re
from typing import Dict, List, Tuple

KEYWORDS: Dict[str, List[str]] = {
    "Insurance": ["insurance", "policy", "premium", "insured", "sum insured", "nominee", "irdai", "idv", "claim"],
    "ID": ["aadhaar", "aadhar", "passport", "pan card", "permanent account number", "voter", "driving licence",
           "driving license", "identity card", "date of birth", "dob", "republic of india", "unique identification"],
    "Certificate": ["certificate", "certify", "certified", "degree", "diploma", "marks", "university",
                    "convocation", "awarded", "board of", "completion", "course", "grade"],
    "Bill": ["invoice", "bill no", "bill date", "amount due", "due date", "units consumed", "tax invoice",
             "electricity", "water bill", "gst", "total payable", "meter", "broadband bill"],
    "Warranty": ["warranty", "guarantee", "serial no", "serial number", "model no", "date of purchase",
                 "authorized service", "authorised service", "manufacturing defect"],
    "Vehicle": ["registration certificate", "rc book", "chassis", "engine no", "puc", "pollution under control",
                "fitness certificate", "road tax", "vehicle", "regn", "motor vehicle"],
    "Subscription": ["subscription", "renewal", "billing cycle", "auto-renew", "auto renew", "plan", "membership",
                     "next billing", "monthly plan", "annual plan", "streaming"],
}


def score_types(text: str) -> Dict[str, int]:
    t = text.lower()
    scores = {}
    for doc_type, words in KEYWORDS.items():
        scores[doc_type] = sum(len(re.findall(re.escape(w), t)) for w in words)
    return scores


def classify(text: str, filename: str = "") -> Tuple[str, float]:
    """Return (type, confidence 0-1). Filename hints count double."""
    scores = score_types(text)
    name = filename.lower().replace("_", " ").replace("-", " ")
    for doc_type, words in KEYWORDS.items():
        scores[doc_type] += 2 * sum(1 for w in words if w in name)
    total = sum(scores.values())
    if total == 0:
        return "Other", 0.0
    best = max(scores, key=scores.get)
    return best, round(scores[best] / total, 2)


def train_ml_classifier(texts: List[str], labels: List[str]):
    """Optional ML: needs scikit-learn (`pip install scikit-learn`).

    pipeline = train_ml_classifier(texts, labels); pipeline.predict([new_text])
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.pipeline import make_pipeline

    model = make_pipeline(TfidfVectorizer(stop_words="english", ngram_range=(1, 2)), MultinomialNB())
    model.fit(texts, labels)
    return model
