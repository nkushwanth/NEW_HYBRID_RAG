import pickle
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from langchain_cohere import CohereRerank
from langchain_classic.retrievers import ContextualCompressionRetriever
from qdrant_client.http import models as qdrant_models

class RetrieverBuilder:
    def __init__(self, config, embeddings):
        self.config = config
        self.embeddings = embeddings
        self.client = QdrantClient(host=config.QDRANT_HOST, port=config.QDRANT_PORT)
    
    def build(self):
        vectorstore = QdrantVectorStore(
            client=self.client,
            collection_name=self.config.QDRANT_COLLECTION,
            embedding=self.embeddings
        )
        
        # Filter for parent chunks
        filter_condition = qdrant_models.Filter(
            must=[
                qdrant_models.FieldCondition(
                    key="metadata.chunk_type",
                    match=qdrant_models.MatchValue(value="parent")
                )
            ]
        )
        
        vector_retriever = vectorstore.as_retriever(
            search_kwargs={"k": self.config.RETRIEVAL_K, "filter": filter_condition}
        )
        
        # Load BM25
        bm25_path = self.config.CACHE_DIR / self.config.BM25_FILE
        with open(bm25_path, "rb") as f:
            bm25_retriever = pickle.load(f)
        bm25_retriever.k = self.config.RETRIEVAL_K
        
        # Hybrid retriever
        hybrid_retriever = EnsembleRetriever(
            retrievers=[bm25_retriever, vector_retriever],
            weights=[0.5, 0.5]
        )
        
        # Reranker
        reranker = CohereRerank(
            model="rerank-english-v3.0",
            top_n=self.config.RERANK_TOP_N
        )
        
        return ContextualCompressionRetriever(
            base_retriever=hybrid_retriever,
            base_compressor=reranker
        )