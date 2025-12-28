from pathlib import Path
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

BASE_DIR = Path.home() / "Desktop" / "FSQ_Regulations_PoC"
ART_DIR = BASE_DIR / "03_Articles"
VEC_DIR = BASE_DIR / "04_VectorStore"

VEC_DIR.mkdir(exist_ok=True)

docs = []

# すべての条文txtを読み込む
for txt in ART_DIR.rglob("*.txt"):
    loader = TextLoader(str(txt), encoding="utf-8")
    for d in loader.load():
        d.metadata["source"] = txt.name
        d.metadata["path"] = str(txt)
        docs.append(d)

print(f"Loaded {len(docs)} article documents")

# Embedding
emb = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# 🔴 ここが重要：load_local ではなく from_documents
db = FAISS.from_documents(docs, emb)

# 保存
db.save_local(str(VEC_DIR))

print("✅ Vector store created and saved to:", VEC_DIR)
