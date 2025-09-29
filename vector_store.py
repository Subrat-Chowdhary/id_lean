"""
Vector Store Manager for RAG Pipeline
Handles document embeddings and similarity search
"""

import chromadb
from typing import List, Dict, Any, Optional

import requests


class OllamaEmbeddingClient:
    """Generate embeddings using a locally running Ollama server."""

    def __init__(self, model_name: str = "nomic-embed-text", base_url: Optional[str] = None, timeout: int = 60):
        self.model_name = model_name
        self.base_url = (base_url or "http://localhost:11434").rstrip("/")
        self.timeout = timeout

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        embeddings: List[List[float]] = []
        for text in texts:
            embeddings.append(self._embed_single(text))
        return embeddings

    def _embed_single(self, text: str) -> List[float]:
        payload = {"model": self.model_name, "prompt": text}
        url = f"{self.base_url}/api/embeddings"

        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as exc:
            raise RuntimeError(
                f"Failed to contact Ollama embeddings endpoint at {url}. "
                "Ensure Ollama is running (`ollama serve`) and the model is pulled."
            ) from exc

        if "error" in data:
            raise RuntimeError(f"Ollama returned an error for embeddings request: {data['error']}")

        embedding = data.get("embedding")
        if embedding is None:
            raise RuntimeError("Ollama response did not include an 'embedding' field.")

        return embedding


class VectorStoreManager:
    """Manages vector embeddings and similarity search for documents"""
    
    def __init__(self, 
                 collection_name: str = "instructional_design_docs",
                 model_name: str = "nomic-embed-text",
                 persist_directory: str = "chroma_db",
                 ollama_url: Optional[str] = None):
        
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        
        # Initialize embedding model
        self.embedding_model = OllamaEmbeddingClient(model_name, base_url=ollama_url)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(collection_name)
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "Instructional Design Documents"}
            )
    
    def add_document(self, 
                    document_data: Dict[str, Any], 
                    document_id: Optional[str] = None) -> str:
        """
        Add a processed document to the vector store
        
        Args:
            document_data: Processed document data from DocumentProcessor
            document_id: Optional custom document ID
            
        Returns:
            Document ID in the vector store
        """
        if document_id is None:
            document_id = self._generate_document_id(document_data['file_path'])
        
        # Extract chunks and metadata
        chunks = document_data['metadata']['chunks']
        base_metadata = {
            'filename': document_data['metadata']['filename'],
            'file_type': document_data['metadata']['file_type'],
            'file_size': document_data['metadata']['file_size'],
            'document_id': document_id
        }
        
        # Prepare data for ChromaDB
        chunk_ids = []
        chunk_texts = []
        chunk_metadatas = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{document_id}_chunk_{i}"
            chunk_ids.append(chunk_id)
            chunk_texts.append(chunk)
            
            chunk_metadata = base_metadata.copy()
            chunk_metadata.update({
                'chunk_index': i,
                'chunk_id': chunk_id,
                'chunk_length': len(chunk)
            })
            chunk_metadatas.append(chunk_metadata)
        
        # Generate embeddings
        embeddings = self.embedding_model.embed_texts(chunk_texts)
        
        # Add to ChromaDB
        self.collection.add(
            ids=chunk_ids,
            embeddings=embeddings,
            documents=chunk_texts,
            metadatas=chunk_metadatas
        )
        
        return document_id
    
    def search(self, 
               query: str, 
               n_results: int = 5,
               filter_metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Search for relevant document chunks
        
        Args:
            query: Search query
            n_results: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            Search results with chunks and metadata
        """
        # Generate query embedding
        query_embedding = self.embedding_model.embed_texts([query])
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            where=filter_metadata
        )
        
        # Process results
        processed_results = []
        
        for i in range(len(results['ids'][0])):
            result = {
                'chunk_id': results['ids'][0][i],
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'similarity_score': 1 - results['distances'][0][i]  # Convert distance to similarity
            }
            processed_results.append(result)
        
        return {
            'query': query,
            'results': processed_results,
            'total_results': len(processed_results)
        }
    
    def get_documents_by_type(self, file_type: str) -> List[Dict[str, Any]]:
        """Get all documents of a specific type"""
        results = self.collection.get(
            where={"file_type": file_type}
        )
        
        # Group by document_id
        documents = {}
        for i, chunk_id in enumerate(results['ids']):
            doc_id = results['metadatas'][i]['document_id']
            if doc_id not in documents:
                documents[doc_id] = {
                    'document_id': doc_id,
                    'filename': results['metadatas'][i]['filename'],
                    'file_type': results['metadatas'][i]['file_type'],
                    'chunks': []
                }
            
            documents[doc_id]['chunks'].append({
                'chunk_id': chunk_id,
                'text': results['documents'][i],
                'metadata': results['metadatas'][i]
            })
        
        return list(documents.values())
    
    def delete_document(self, document_id: str) -> bool:
        """Delete a document and all its chunks"""
        try:
            # Get all chunks for this document
            results = self.collection.get(
                where={"document_id": document_id}
            )
            
            if results['ids']:
                self.collection.delete(ids=results['ids'])
                return True
            return False
            
        except Exception as e:
            print(f"Error deleting document {document_id}: {e}")
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        try:
            count = self.collection.count()
            
            # Get sample of documents to analyze
            sample_results = self.collection.get(limit=min(100, count))
            
            # Analyze file types
            file_types = {}
            documents = set()
            
            for metadata in sample_results['metadatas']:
                file_type = metadata.get('file_type', 'unknown')
                file_types[file_type] = file_types.get(file_type, 0) + 1
                documents.add(metadata.get('document_id', 'unknown'))
            
            return {
                'total_chunks': count,
                'unique_documents': len(documents),
                'file_types': file_types,
                'collection_name': self.collection_name
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def semantic_search(self, 
                       query: str, 
                       context_type: str = None,
                       n_results: int = 10) -> List[Dict[str, Any]]:
        """
        Enhanced semantic search with context awareness
        
        Args:
            query: Search query
            context_type: Type of content needed (e.g., 'training', 'assessment', 'theory')
            n_results: Number of results to return
            
        Returns:
            Contextually relevant search results
        """
        # Enhance query with context
        enhanced_query = query
        if context_type:
            enhanced_query = f"{context_type} {query}"
        
        # Perform search
        search_results = self.search(enhanced_query, n_results)
        
        # Group related chunks
        grouped_results = self._group_related_chunks(search_results['results'])
        
        return grouped_results
    
    def _group_related_chunks(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Group related chunks from the same document"""
        document_groups = {}
        
        for result in results:
            doc_id = result['metadata']['document_id']
            
            if doc_id not in document_groups:
                document_groups[doc_id] = {
                    'document_id': doc_id,
                    'filename': result['metadata']['filename'],
                    'file_type': result['metadata']['file_type'],
                    'chunks': [],
                    'max_similarity': 0
                }
            
            document_groups[doc_id]['chunks'].append(result)
            document_groups[doc_id]['max_similarity'] = max(
                document_groups[doc_id]['max_similarity'],
                result['similarity_score']
            )
        
        # Sort by max similarity
        grouped_results = sorted(
            document_groups.values(),
            key=lambda x: x['max_similarity'],
            reverse=True
        )
        
        return grouped_results
    
    def _generate_document_id(self, file_path: str) -> str:
        """Generate a unique document ID from file path"""
        import hashlib
        return hashlib.md5(file_path.encode()).hexdigest()[:12]
    
    def update_document(self, document_id: str, new_document_data: Dict[str, Any]) -> bool:
        """Update an existing document"""
        # Delete old document
        if self.delete_document(document_id):
            # Add new version
            self.add_document(new_document_data, document_id)
            return True
        return False
