"""ChromaDB 向量存储：支持企业知识库和手动舆情数据"""
from __future__ import annotations
from .document_processor import DocumentChunk


class VectorStore:
    """轻量级 ChromaDB 封装，支持两个集合：知识库 / 舆情数据"""

    def __init__(self, persist_dir: str | None = None):
        import chromadb
        if persist_dir:
            self._client = chromadb.PersistentClient(path=persist_dir)
        else:
            self._client = chromadb.Client()

        self.kb = self._client.get_or_create_collection(
            name="knowledge_base",
            metadata={"hnsw:space": "cosine"},
        )
        self.opinions = self._client.get_or_create_collection(
            name="opinions",
            metadata={"hnsw:space": "cosine"},
        )

    # ---- 知识库操作 ----
    def add_to_knowledge_base(self, chunks: list[DocumentChunk]) -> int:
        if not chunks:
            return 0
        ids = [f"kb_{c.metadata['source']}_{c.metadata['chunk_id']}" for c in chunks]
        self.kb.upsert(
            ids=ids,
            documents=[c.content for c in chunks],
            metadatas=[c.metadata for c in chunks],
        )
        return len(chunks)

    def query_knowledge_base(self, query: str, n_results: int = 3) -> list[str]:
        if self.kb.count() == 0:
            return []
        try:
            results = self.kb.query(query_texts=[query], n_results=min(n_results, self.kb.count()))
            return results["documents"][0] if results["documents"] else []
        except Exception:
            return []

    # ---- 舆情数据操作 ----
    def add_opinions(self, texts: list[str], metadata_list: list[dict] | None = None) -> int:
        if not texts:
            return 0
        base = self.opinions.count()
        ids = [f"op_{base + i}" for i in range(len(texts))]
        metas = metadata_list or [{"source": "manual_input"} for _ in texts]
        self.opinions.upsert(ids=ids, documents=texts, metadatas=metas)
        return len(texts)

    def query_opinions(self, query: str, n_results: int = 5) -> list[str]:
        if self.opinions.count() == 0:
            return []
        try:
            results = self.opinions.query(query_texts=[query], n_results=min(n_results, self.opinions.count()))
            return results["documents"][0] if results["documents"] else []
        except Exception:
            return []

    def get_all_opinions(self) -> list[str]:
        if self.opinions.count() == 0:
            return []
        try:
            results = self.opinions.get()
            return results["documents"] if results["documents"] else []
        except Exception:
            return []

    def clear_knowledge_base(self):
        self._client.delete_collection("knowledge_base")
        self.kb = self._client.get_or_create_collection(
            name="knowledge_base", metadata={"hnsw:space": "cosine"},
        )

    def clear_opinions(self):
        self._client.delete_collection("opinions")
        self.opinions = self._client.get_or_create_collection(
            name="opinions", metadata={"hnsw:space": "cosine"},
        )

    @property
    def kb_count(self) -> int:
        return self.kb.count()

    @property
    def opinion_count(self) -> int:
        return self.opinions.count()
