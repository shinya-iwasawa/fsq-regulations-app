from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

BASE_DIR = Path.home() / "Desktop" / "FSQ_Regulations_PoC"
VEC_DIR = BASE_DIR / "04_VectorStore"

# Embedding
emb = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# VectorStore 読み込み
db = FAISS.load_local(
    str(VEC_DIR),
    emb,
    allow_dangerous_deserialization=True
)

def judge_item_simple(item: str, k: int = 5):
    docs = db.similarity_search(item, k=k)

    if not docs:
        return {
            "result": "unknown",
            "reason": "No relevant regulation found",
            "evidence_article_ids": []
        }

    article_ids = [d.metadata["source"] for d in docs]

    return {
        "result": "unknown",  # ← PoCではまず unknown を正解にする
        "reason": f"Relevant articles found but no explicit permission or prohibition detected for '{item}'.",
        "evidence_article_ids": article_ids
    }

if __name__ == "__main__":
    target = "crab extract"
    print("Judging:", target)
    res = judge_item_simple(target)
    print(res)
