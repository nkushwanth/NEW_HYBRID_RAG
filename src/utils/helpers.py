import redis
import uuid
from typing import Optional, Dict, Any

class SessionManager:
    def __init__(self, redis_client):
        self.redis_client = redis_client
        self.session_id = str(uuid.uuid4())[:8]
    
    def get_conversation_context(self, max_messages=16):
        """Get recent conversation history"""
        history = self.redis_client.lrange(
            f"session:{self.session_id}:conv",
            -max_messages, -1
        )
        if not history:
            return ""
        
        context = "\nPrevious conversation:\n"
        for msg in history:
            context += f"{msg}\n"
        return context
    
    def add_to_conversation(self, user_msg, assistant_msg, ttl=3600):
        """Add exchange to conversation history"""
        key = f"session:{self.session_id}:conv"
        self.redis_client.rpush(
            key,
            f"User: {user_msg}",
            f"Assistant: {assistant_msg}"
        )
        self.redis_client.expire(key, ttl)
    
    def clear_conversation(self):
        """Clear conversation history"""
        self.redis_client.delete(f"session:{self.session_id}:conv")
    
    def get_conversation_length(self):
        """Get number of messages in conversation"""
        return self.redis_client.llen(f"session:{self.session_id}:conv")
    
    def check_rate_limit(self, max_requests=10, window=60):
        """Check rate limit for current session"""
        key = f"rate:{self.session_id}"
        current = self.redis_client.incr(key)
        if current == 1:
            self.redis_client.expire(key, window)
        return current <= max_requests

def get_redis_client(host="localhost", port=6379):
    """Get Redis client"""
    return redis.Redis(host=host, port=port, decode_responses=True)

def format_time(seconds):
    """Format time in seconds to human-readable string"""
    if seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"