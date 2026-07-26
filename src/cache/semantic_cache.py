import redis
from redisvl.utils.vectorize import HFTextVectorizer
from redisvl.extensions.cache.llm import SemanticCache

class SemanticCacheWrapper:
    """
    Wrapper for RedisVL SemanticCache
    """
    def __init__(self, redis_client, model_name, threshold=0.1, ttl=3600):
        self.redis_client = redis_client
        self.threshold = threshold
        self.ttl = ttl
        
        try:
            vectorizer = HFTextVectorizer(model=model_name)
            self.cache = SemanticCache(
                name="langchain_semantic_cache",
                redis_client=redis_client,
                vectorizer=vectorizer,
                threshold=threshold,
                ttl=ttl
            )
            self._print_status()
        except Exception as e:
            print(f"❌ Error setting up RedisVL cache: {e}")
            self.cache = None
    
    def _print_status(self):
        print("✅ RedisVL Semantic Cache Initialized")
        print(f"   - Cache name: langchain_semantic_cache")
        print(f"   - Threshold: {self.threshold}")
        print(f"   - TTL: {self.ttl}s")
    
    def check(self, query):
        """Check cache and return string response"""
        if not self.cache:
            return None
        
        try:
            results = self.cache.check(query)
            if results:
                # Handle different result formats
                if isinstance(results, str):
                    return results
                elif isinstance(results, list) and len(results) > 0:
                    return results[0].get('response', str(results[0]))
                elif isinstance(results, dict):
                    return results.get('response', str(results))
                else:
                    return str(results)
            return None
        except Exception as e:
            print(f"⚠️ Cache lookup error: {e}")
            return None
    
    def store(self, query, response):
        """Store in cache"""
        if not self.cache:
            return False
        
        try:
            if not isinstance(response, str):
                response = str(response)
            self.cache.store(query, response)
            return True
        except Exception as e:
            print(f"⚠️ Cache store error: {e}")
            return False
    
    def clear(self):
        """Clear the cache"""
        if self.cache:
            try:
                self.cache.clear()
                print("🧹 Cache cleared")
            except Exception as e:
                print(f"❌ Error clearing cache: {e}")
    
    def get_stats(self):
        """Get cache statistics"""
        if not self.cache:
            return {"error": "Cache not initialized"}
        
        try:
            keys = self.redis_client.keys("langchain_semantic_cache:*")
            return {
                "total_entries": len(keys),
                "threshold": self.threshold,
                "ttl": self.ttl
            }
        except Exception as e:
            return {"error": str(e)}