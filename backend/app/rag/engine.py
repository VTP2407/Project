import re
import math
from typing import List, Dict, Any, Optional
from collections import Counter
from sqlalchemy.orm import Session
from app.models.entities import KnowledgeDocument, KnowledgeChunk

class RAGEngine:
    """
    Retrieval-Augmented Generation Engine supporting authoritative medical document
    ingestion, semantic chunking, cosine vector similarity search, and evidence formatting.
    """
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 400, overlap: int = 50) -> List[str]:
        words = text.split()
        if not words:
            return []
        chunks = []
        start = 0
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk = " ".join(words[start:end])
            chunks.append(chunk)
            if end == len(words):
                break
            start += chunk_size - overlap
        return chunks

    @staticmethod
    def compute_embedding(text: str) -> Dict[str, float]:
        """Term-frequency vector embedding with normalization."""
        words = re.findall(r"\w+", text.lower())
        if not words:
            return {}
        counts = Counter(words)
        total = math.sqrt(sum(v * v for v in counts.values()))
        return {w: c / total for w, c in counts.items()}

    @staticmethod
    def cosine_similarity(v1: Dict[str, float], v2: Dict[str, float]) -> float:
        if not v1 or not v2:
            return 0.0
        # Dot product of normalized term vectors
        common = set(v1.keys()) & set(v2.keys())
        return sum(v1[k] * v2[k] for k in common)

    @classmethod
    def search_knowledge(
        cls, db: Session, query: str, category: Optional[str] = None, top_k: int = 3, min_score: float = 0.08
    ) -> List[Dict[str, Any]]:
        """Semantic vector retrieval over Knowledge Chunks."""
        q_vec = cls.compute_embedding(query)
        
        chunk_query = db.query(KnowledgeChunk, KnowledgeDocument).join(
            KnowledgeDocument, KnowledgeChunk.document_id == KnowledgeDocument.id
        )
        if category:
            chunk_query = chunk_query.filter(KnowledgeDocument.category == category)
            
        records = chunk_query.all()
        scored_results = []
        
        for chunk, doc in records:
            chunk_vec = chunk.embedding_json or cls.compute_embedding(chunk.content)
            score = cls.cosine_similarity(q_vec, chunk_vec)
            if score >= min_score:
                scored_results.append({
                    "doc_id": doc.doc_id,
                    "title": doc.title,
                    "category": doc.category,
                    "source": doc.source,
                    "chunk_id": chunk.id,
                    "content": chunk.content,
                    "similarity_score": round(float(score), 4)
                })
                
        scored_results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return scored_results[:top_k]

    @classmethod
    def format_rag_context(cls, results: List[Dict[str, Any]]) -> str:
        if not results:
            return "Không có tài liệu tham khảo y khoa trực tiếp phù hợp trong cơ sở tri thức."
        
        context_parts = []
        for i, res in enumerate(results, 1):
            context_parts.append(
                f"[{i}] {res['title']} (Nguồn: {res['source']} - {res['category']}):\n\"{res['content']}\""
            )
        return "\n\n".join(context_parts)

