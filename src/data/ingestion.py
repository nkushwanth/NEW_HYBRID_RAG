import hashlib
import pickle
import time
from pathlib import Path
from tqdm import tqdm

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.retrievers import BM25Retriever
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance
from langchain_qdrant import QdrantVectorStore

class DocumentIngestor:
    def __init__(self, config, embeddings):
        self.config = config
        self.embeddings = embeddings
        self.client = QdrantClient(host=config.QDRANT_HOST, port=config.QDRANT_PORT)
        self.hash_file = config.CACHE_DIR / "processed_hashes.pkl"
        self.processed_hashes = self._load_hashes()
    
    def _load_hashes(self):
        if self.hash_file.exists():
            with open(self.hash_file, "rb") as f:
                return pickle.load(f)
        return set()
    
    def _save_hashes(self):
        with open(self.hash_file, "wb") as f:
            pickle.dump(self.processed_hashes, f)
    
    def _hierarchical_chunking(self, documents):
        parent_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.PARENT_CHUNK_SIZE,
            chunk_overlap=self.config.PARENT_CHUNK_OVERLAP
        )
        child_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.CHILD_CHUNK_SIZE,
            chunk_overlap=self.config.CHILD_CHUNK_OVERLAP
        )
        
        parent_chunks = parent_splitter.split_documents(documents)
        all_chunks = []
        
        for idx, parent in enumerate(parent_chunks):
            parent.metadata["chunk_type"] = "parent"
            parent.metadata["chunk_id"] = f"parent_{idx}"
            all_chunks.append(parent)
            
            children = child_splitter.split_documents([parent])
            for child_idx, child in enumerate(children):
                child.metadata["chunk_type"] = "child"
                child.metadata["parent_id"] = f"parent_{idx}"
                child.metadata["child_idx"] = child_idx
                all_chunks.append(child)
        
        return all_chunks
    
    def ingest(self):
        pdf_files = list(self.config.PDF_DIR.glob("*.pdf"))
        if not pdf_files:
            print("⚠️ No PDF files found!")
            return False
        
        documents = []
        print(f"📁 Loading {len(pdf_files)} PDF files...")
        
        for pdf_file in tqdm(pdf_files, desc="Loading PDFs"):
            with open(pdf_file, "rb") as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            
            if file_hash in self.processed_hashes:
                print(f"⏭️ Skipping {pdf_file.name} (already processed)")
                continue
            
            loader = PyMuPDFLoader(str(pdf_file))
            docs = loader.load()
            for doc in docs:
                doc.metadata["source_file"] = pdf_file.name
                doc.metadata["title"] = pdf_file.stem
            documents.extend(docs)
            self.processed_hashes.add(file_hash)
        
        if not documents:
            print("⚠️ No new documents to process!")
            return False
        
        chunks = self._hierarchical_chunking(documents)
        print(f"🧩 Total chunks: {len(chunks)}")
        
        # Check if Qdrant is running
        try:
            collections = [c.name for c in self.client.get_collections().collections]
            print(f"✅ Connected to Qdrant. Existing collections: {collections}")
        except Exception as e:
            print(f"❌ Cannot connect to Qdrant: {e}")
            print("💡 Make sure Qdrant is running: docker run -p 6333:6333 qdrant/qdrant")
            return False
        
        # Create collection if it doesn't exist
        if self.config.QDRANT_COLLECTION not in collections:
            print(f"🆕 Creating new collection: {self.config.QDRANT_COLLECTION}")
            test_embedding = self.embeddings.embed_query("test")
            self.client.create_collection(
                collection_name=self.config.QDRANT_COLLECTION,
                vectors_config=VectorParams(
                    size=len(test_embedding),
                    distance=Distance.COSINE
                )
            )
            print(f"✅ Collection created successfully")
        
        # Create vector store
        vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=self.config.QDRANT_COLLECTION,
            embedding=self.embeddings
        )
        
        # Upload with smaller batches and progress
        BATCH_SIZE = 10  # Smaller batches to avoid timeout
        total_batches = (len(chunks) + BATCH_SIZE - 1) // BATCH_SIZE
        
        print(f"📤 Adding {len(chunks)} chunks in {total_batches} batches of {BATCH_SIZE}...")
        
        with tqdm(total=len(chunks), desc="Uploading chunks") as pbar:
            for i in range(0, len(chunks), BATCH_SIZE):
                batch = chunks[i:i+BATCH_SIZE]
                try:
                    vector_store.add_documents(batch)
                    pbar.update(len(batch))
                except Exception as e:
                    print(f"\n❌ Error uploading batch {i//BATCH_SIZE + 1}: {e}")
                    print("💡 Retrying with smaller batch...")
                    # Try smaller batch
                    for doc in batch:
                        try:
                            vector_store.add_documents([doc])
                            pbar.update(1)
                        except Exception as e2:
                            print(f"❌ Failed to upload document: {e2}")
                            continue
        
        print("💾 Saving BM25 retriever...")
        try:
            bm25 = BM25Retriever.from_documents(chunks)
            bm25_path = self.config.CACHE_DIR / self.config.BM25_FILE
            with open(bm25_path, "wb") as f:
                pickle.dump(bm25, f)
            print(f"✅ BM25 saved to: {bm25_path}")
        except Exception as e:
            print(f"❌ Error saving BM25: {e}")
        
        self._save_hashes()
        print("✅ Ingestion Complete!")
        
        # Verify
        try:
            collection_info = self.client.get_collection(
                collection_name=self.config.QDRANT_COLLECTION
            )
            print(f"\n📊 Collection Stats:")
            print(f"  - Collection: {self.config.QDRANT_COLLECTION}")
            print(f"  - Points in Qdrant: {collection_info.points_count}")
            print(f"  - Total chunks: {len(chunks)}")
        except Exception as e:
            print(f"⚠️ Could not verify collection: {e}")
        
        return True