import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # API Keys
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    COHERE_API_KEY = os.getenv("COHERE_API_KEY")
    HF_TOKEN = os.getenv("HF_TOKEN")
    
    # Redis
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    
    # Qdrant
    QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
    
    # Paths
    PDF_DIR = Path(os.getenv("PDF_DIR", "./data/pdfs"))
    CACHE_DIR = Path(os.getenv("CACHE_DIR", "./cache"))
    
    # Collections
    QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "raga_documents")
    BM25_FILE = os.getenv("BM25_FILE", "bm25.pkl")
    
    # Embeddings
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    
    # LLM
    LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", 0.3))
    
    # Cache
    CACHE_THRESHOLD = float(os.getenv("CACHE_THRESHOLD", 0.1))
    CACHE_TTL = int(os.getenv("CACHE_TTL", 3600))
    
    # Retrieval
    RETRIEVAL_K = int(os.getenv("RETRIEVAL_K", 20))
    RERANK_TOP_N = int(os.getenv("RERANK_TOP_N", 5))
    
    # Chunking
    PARENT_CHUNK_SIZE = int(os.getenv("PARENT_CHUNK_SIZE", 1500))
    PARENT_CHUNK_OVERLAP = int(os.getenv("PARENT_CHUNK_OVERLAP", 200))
    CHILD_CHUNK_SIZE = int(os.getenv("CHILD_CHUNK_SIZE", 500))
    CHILD_CHUNK_OVERLAP = int(os.getenv("CHILD_CHUNK_OVERLAP", 50))
    
    # Rate limiting
    RATE_LIMIT_MAX = int(os.getenv("RATE_LIMIT_MAX", 10))
    RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", 60))

# Create directories if they don't exist
Config.CACHE_DIR.mkdir(exist_ok=True)
Config.PDF_DIR.mkdir(exist_ok=True)