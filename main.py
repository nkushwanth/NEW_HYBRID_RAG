import time
from langchain_huggingface import HuggingFaceEmbeddings

from src.config import Config
from src.cache.semantic_cache import SemanticCacheWrapper
from src.data.ingestion import DocumentIngestor
from src.retrieval.retriever import RetrieverBuilder
from src.rag.chain import RAGChain
from src.utils.helpers import SessionManager, get_redis_client

def main():
    # Initialize components
    config = Config()
    redis_client = get_redis_client(config.REDIS_HOST, config.REDIS_PORT)
    session_manager = SessionManager(redis_client)
    
    # Embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name=config.EMBEDDING_MODEL,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    # Semantic Cache
    semantic_cache = SemanticCacheWrapper(
        redis_client=redis_client,
        model_name=config.EMBEDDING_MODEL,
        threshold=config.CACHE_THRESHOLD,
        ttl=config.CACHE_TTL
    )
    
    # Data ingestion (uncomment to run
    ingestor = DocumentIngestor(config, embeddings)
    ingestor.ingest()
    
    # Build retriever and RAG chain
    retriever_builder = RetrieverBuilder(config, embeddings)
    retriever = retriever_builder.build()
    
    rag = RAGChain(config, retriever)
    rag.set_conversation_context(session_manager.get_conversation_context)
    rag_chain = rag.create_chain()
    
    # Main loop
    print(f"\n{'='*60}")
    print(f"SESSION: {session_manager.session_id}")
    print("Commands: /clear, /stats, /cache_stats, /clear_cache, quit")
    print('='*60)
    
    while True:
        query = input("\n❓ You: ")
        
        if query.lower() in ["quit", "exit"]:
            break
        elif query == "/clear":
            session_manager.clear_conversation()
            print("✅ Conversation cleared")
        elif query == "/stats":
            conv_count = session_manager.get_conversation_length()
            print(f"📊 Conversation history: {conv_count} messages")
        elif query == "/cache_stats":
            stats = semantic_cache.get_stats()
            print(f"📊 Cache stats: {stats}")
        elif query == "/clear_cache":
            semantic_cache.clear()
        else:
            # Rate limit check
            if not session_manager.check_rate_limit(config.RATE_LIMIT_MAX, config.RATE_LIMIT_WINDOW):
                print("⚠️ Rate limit exceeded. Please wait a minute.")
                continue
            
            print("\n🤖 Bot:")
            print("-" * 60)
            
            start = time.time()
            
            # Check cache
            cached_response = semantic_cache.check(query)
            if cached_response:
                print("⚡ Semantic cache hit!\n")
                print(cached_response)
                print("-" * 60)
                session_manager.add_to_conversation(query, cached_response)
                print(f"\n⏱️ Time: {time.time()-start:.2f}s")
                continue
            
            # Generate response
            print("🔄 Generating...\n")
            answer = rag_chain.invoke(query)
            print(answer)
            print("-" * 60)
            
            # Store in cache
            semantic_cache.store(query, answer)
            
            session_manager.add_to_conversation(query, answer)
            print(f"\n⏱️ Time: {time.time()-start:.2f}s")

if __name__ == "__main__":
    main()
