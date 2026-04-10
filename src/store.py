from __future__ import annotations

from typing import Any, Callable

from .chunking import _dot
from .embeddings import _mock_embed
from .models import Document


class EmbeddingStore:
    """
    A vector store for text chunks.

    Tries to use ChromaDB if available; falls back to an in-memory store.
    The embedding_fn parameter allows injection of mock embeddings for tests.
    """

    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
        persist_directory: str | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._use_chroma = False
        self._store: list[dict[str, Any]] = []
        self._collection = None
        self._next_index = 0

        try:
            import chromadb  # noqa: F401

            # Initialize chromadb client + collection
            # If persist_directory is provided, use PersistentClient for disk storage
            # Otherwise, use in-memory Client (default for tests)
            if persist_directory:
                client = chromadb.PersistentClient(path=persist_directory)
            else:
                client = chromadb.Client()
            
            # Delete existing collection if it exists (for clean tests)
            try:
                client.delete_collection(name=collection_name)
            except Exception:
                pass
            
            self._collection = client.create_collection(name=collection_name)
            self._use_chroma = True
        except Exception:
            self._use_chroma = False
            self._collection = None

    def _make_record(self, doc: Document) -> dict[str, Any]:
        # Build a normalized stored record for one document
        embedding = self._embedding_fn(doc.content)
        return {
            "id": doc.id,
            "content": doc.content,
            "embedding": embedding,
            "metadata": doc.metadata,
        }

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        # Run in-memory similarity search over provided records
        if not records:
            return []
        
        query_embedding = self._embedding_fn(query)
        
        # Compute similarity scores for all records
        scored_records = []
        for record in records:
            score = _dot(query_embedding, record["embedding"])
            scored_records.append({
                "content": record["content"],
                "score": score,
                "metadata": record.get("metadata", {}),
            })
        
        # Sort by score descending and return top_k
        scored_records.sort(key=lambda x: x["score"], reverse=True)
        return scored_records[:top_k]

    def add_documents(self, docs: list[Document]) -> None:
        """
        Embed each document's content and store it.

        For ChromaDB: use collection.upsert(ids=[...], documents=[...], embeddings=[...])
        For in-memory: append dicts to self._store
        """
        if not docs:
            return
        
        if self._use_chroma and self._collection is not None:
            # Use ChromaDB with upsert (allows duplicate IDs)
            ids = []
            documents = []
            embeddings = []
            metadatas = []
            
            for doc in docs:
                embedding = self._embedding_fn(doc.content)
                # Make ID unique by appending counter
                unique_id = f"{doc.id}_{self._next_index}"
                self._next_index += 1
                
                ids.append(unique_id)
                documents.append(doc.content)
                embeddings.append(embedding)
                
                # ChromaDB requires non-empty metadata dict
                # Add dummy field if metadata is empty
                metadata = doc.metadata.copy() if doc.metadata else {}
                if not metadata:
                    metadata["_dummy"] = "true"
                # Store original doc_id in metadata for filtering
                metadata["_original_id"] = doc.id
                metadatas.append(metadata)
            
            self._collection.upsert(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
            )
        else:
            # Use in-memory store
            for doc in docs:
                record = self._make_record(doc)
                self._store.append(record)

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Find the top_k most similar documents to query.

        For in-memory: compute dot product of query embedding vs all stored embeddings.
        """
        if self._use_chroma and self._collection is not None:
            # Use ChromaDB
            query_embedding = self._embedding_fn(query)
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
            )
            
            # Format results
            # ChromaDB returns distances (lower is better), convert to similarity scores (higher is better)
            formatted_results = []
            if results["documents"] and results["documents"][0]:
                for i, content in enumerate(results["documents"][0]):
                    # Convert distance to similarity: similarity = -distance
                    # This makes higher scores better (consistent with dot product)
                    distance = results["distances"][0][i] if "distances" in results else 0.0
                    similarity = -distance  # Negate distance to get similarity
                    
                    formatted_results.append({
                        "content": content,
                        "score": similarity,
                        "metadata": results["metadatas"][0][i] if "metadatas" in results else {},
                    })
            
            # Sort by score descending (higher is better)
            formatted_results.sort(key=lambda x: x["score"], reverse=True)
            return formatted_results
        else:
            # Use in-memory store
            return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        if self._use_chroma and self._collection is not None:
            return self._collection.count()
        else:
            return len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict = None) -> list[dict]:
        """
        Search with optional metadata pre-filtering.

        First filter stored chunks by metadata_filter, then run similarity search.
        """
        if self._use_chroma and self._collection is not None:
            # Use ChromaDB with where filter
            query_embedding = self._embedding_fn(query)
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=metadata_filter if metadata_filter else None,
            )
            
            # Format results
            # ChromaDB returns distances (lower is better), convert to similarity scores (higher is better)
            formatted_results = []
            if results["documents"] and results["documents"][0]:
                for i, content in enumerate(results["documents"][0]):
                    # Convert distance to similarity: similarity = -distance
                    distance = results["distances"][0][i] if "distances" in results else 0.0
                    similarity = -distance
                    
                    formatted_results.append({
                        "content": content,
                        "score": similarity,
                        "metadata": results["metadatas"][0][i] if "metadatas" in results else {},
                    })
            
            # Sort by score descending
            formatted_results.sort(key=lambda x: x["score"], reverse=True)
            return formatted_results
        else:
            # Use in-memory store with manual filtering
            if metadata_filter:
                # Filter records by metadata
                filtered_records = []
                for record in self._store:
                    match = True
                    for key, value in metadata_filter.items():
                        if record.get("metadata", {}).get(key) != value:
                            match = False
                            break
                    if match:
                        filtered_records.append(record)
                return self._search_records(query, filtered_records, top_k)
            else:
                return self._search_records(query, self._store, top_k)

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document.

        Returns True if any chunks were removed, False otherwise.
        """
        if self._use_chroma and self._collection is not None:
            # Use ChromaDB
            try:
                # Get all documents with matching original_id in metadata
                results = self._collection.get(where={"_original_id": doc_id})
                
                if not results["ids"]:
                    return False
                
                # Delete all matching documents
                self._collection.delete(ids=results["ids"])
                return True
            except Exception:
                return False
        else:
            # Use in-memory store
            original_size = len(self._store)
            self._store = [record for record in self._store if record.get("id") != doc_id]
            return len(self._store) < original_size
