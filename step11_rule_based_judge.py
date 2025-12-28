from pathlib import Path
import re
from typing import Dict, List, Tuple

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

# =========================
# Paths
# =========================
BASE_DIR = Path.home() / "Desktop" / "FSQ_Regulations_PoC"
VEC_DIR = BASE_DIR / "04_VectorStore"

# =========================
# Embeddings + VectorStore
# =========================
emb = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

db = FAISS.load_local(
    str(VEC_DIR),
    emb,
    allow_dangerous_deserialization=True
)

# =========================
# Helpers
# =========================
def split_sentences(text: str) -> List[str]:
    text = text.replace("\n", " ")
    parts = re.split(r"(?<=[.;])\s+", text)
    return [p.strip() for p in parts if len(p.strip()) > 20]

def is_definition_or_quality(sentence: str) -> bool:
    s = sentence.lower()
    blacklist = [
        "means",
        "shall be",
        "shall contain",
        "definition",
        "obtained by",
        "consists of",
        "not less than",
        "not more than",
    ]
    return any(b in s for b in blacklist)

# =========================
# Rule patterns
# =========================
PROHIBITED_PATTERNS = [
    r"\bshall\s+not\b",
    r"\bmust\s+not\b",
    r"\bis\s+prohibited\b",
    r"\bno\s+person\s+shall\b",
]

CONDITIONAL_PATTERNS = [
    r"\bsubject\s+to\b",
    r"\bprovided\s+that\b",
    r"\bin\s+accordance\s+with\b",
    r"\bunless\b",
]

ALLOWED_PATTERNS = [
    r"\bmay\s+be\s+used\b",
    r"\bis\s+permitted\b",
]

JP_LABEL = {
    "allowed": "使用可",
    "conditional": "条件付き可",
    "prohibited": "禁止",
    "unknown": "判断不可",
}

def classify_sentence(sentence: str) -> Tuple[str, str]:
    s = sentence.lower()

    for p in PROHIBITED_PATTERNS:
        if re.search(p, s):
            return "prohibited", p
    for p in CONDITIONAL_PATTERNS:
        if re.search(p, s):
            return "conditional", p
    for p in ALLOWED_PATTERNS:
        if re.search(p, s):
            return "allowed", p

    return "unknown", ""

# =========================
# Main judge
# =========================
def judge_item_free(item: str, k: int = 5) -> Dict:
    docs = db.similarity_search(item, k=k)
    item_lc = item.lower()

    if not docs:
        return {
            "item": item,
            "judgement": JP_LABEL["unknown"],
            "reason": "関連条文が見つかりませんでした。",
            "evidence": [],
        }

    matched = []

    for d in docs:
        for sent in split_sentences(d.page_content):
            if item_lc not in sent.lower():
                continue
            if is_definition_or_quality(sent):
                continue

            key, pattern = classify_sentence(sent)
            if key != "unknown":
                return {
                    "item": item,
                    "judgement": JP_LABEL[key],
                    "reason": f"明示表現に一致: {pattern}",
                    "evidence": [{
                        "article_id": d.metadata.get("source", ""),
                        "sentence": sent,
                    }],
                }

            matched.append({
                "article_id": d.metadata.get("source", ""),
                "sentence": sent,
            })

    return {
        "item": item,
        "judgement": JP_LABEL["unknown"],
        "reason": "明示的な使用可／禁止表現が見つかりません。",
        "evidence": matched[:5],
    }

# =========================
# ★ Flask 用ラッパー（これが重要）
# =========================
def rule_based_judge(text: str) -> Dict:
    return judge_item_free(text)

if __name__ == "__main__":
    print(judge_item_free("crab extract"))
