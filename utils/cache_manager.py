import time
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime

class CacheManager:
    """Manages caching for API calls and web scraping to reduce load"""
    
    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = cache_dir
        self.memory_cache = {}
        self.default_ttl = 3600  # 1 hour default TTL
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def get(self, key: str, ttl: Optional[int] = None) -> Optional[Any]:
        """
        Get cached data
        
        Args:
            key: Cache key
            ttl: Time to live in seconds (uses default if None)
            
        Returns:
            Cached data or None if not found/expired
        """
        try:
            # Check memory cache first
            if key in self.memory_cache:
                cache_entry = self.memory_cache[key]
                if self._is_valid(cache_entry, ttl):
                    return cache_entry['data']
                else:
                    # Remove expired entry
                    del self.memory_cache[key]
            
            # Check file cache
            file_path = self._get_cache_file_path(key)
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        cache_entry = json.load(f)
                    
                    if self._is_valid(cache_entry, ttl):
                        # Load back to memory cache
                        self.memory_cache[key] = cache_entry
                        return cache_entry['data']
                    else:
                        # Remove expired file
                        os.remove(file_path)
                except (json.JSONDecodeError, KeyError):
                    # Remove corrupted cache file
                    os.remove(file_path)
            
            return None
            
        except Exception as e:
            print(f"Cache get error for key {key}: {e}")
            return None
    
    def set(self, key: str, data: Any, ttl: Optional[int] = None) -> bool:
        """
        Set cached data
        
        Args:
            key: Cache key
            data: Data to cache
            ttl: Time to live in seconds (uses default if None)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if ttl is None:
                ttl = self.default_ttl
            
            cache_entry = {
                'data': data,
                'timestamp': time.time(),
                'ttl': ttl
            }
            
            # Store in memory cache
            self.memory_cache[key] = cache_entry
            
            # Store in file cache for persistence
            file_path = self._get_cache_file_path(key)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(cache_entry, f, default=str, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Cache set error for key {key}: {e}")
            return False
    
    def invalidate(self, key: str) -> bool:
        """
        Invalidate cached data
        
        Args:
            key: Cache key to invalidate
            
        Returns:
            True if successful
        """
        try:
            # Remove from memory cache
            if key in self.memory_cache:
                del self.memory_cache[key]
            
            # Remove from file cache
            file_path = self._get_cache_file_path(key)
            if os.path.exists(file_path):
                os.remove(file_path)
            
            return True
            
        except Exception as e:
            print(f"Cache invalidate error for key {key}: {e}")
            return False
    
    def clear_all(self) -> bool:
        """Clear all cached data"""
        try:
            # Clear memory cache
            self.memory_cache.clear()
            
            # Clear file cache
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.cache_dir, filename)
                    os.remove(file_path)
            
            return True
            
        except Exception as e:
            print(f"Cache clear error: {e}")
            return False
    
    def cleanup_expired(self) -> int:
        """
        Clean up expired cache entries
        
        Returns:
            Number of entries cleaned up
        """
        cleaned_count = 0
        
        try:
            # Clean memory cache
            expired_keys = []
            for key, cache_entry in self.memory_cache.items():
                if not self._is_valid(cache_entry):
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.memory_cache[key]
                cleaned_count += 1
            
            # Clean file cache
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.cache_dir, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            cache_entry = json.load(f)
                        
                        if not self._is_valid(cache_entry):
                            os.remove(file_path)
                            cleaned_count += 1
                            
                    except (json.JSONDecodeError, KeyError):
                        # Remove corrupted files
                        os.remove(file_path)
                        cleaned_count += 1
            
            return cleaned_count
            
        except Exception as e:
            print(f"Cache cleanup error: {e}")
            return cleaned_count
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        try:
            memory_count = len(self.memory_cache)
            
            file_count = 0
            total_file_size = 0
            
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    file_count += 1
                    file_path = os.path.join(self.cache_dir, filename)
                    total_file_size += os.path.getsize(file_path)
            
            return {
                'memory_entries': memory_count,
                'file_entries': file_count,
                'total_file_size_mb': round(total_file_size / (1024 * 1024), 2),
                'cache_directory': self.cache_dir
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _is_valid(self, cache_entry: Dict, ttl: Optional[int] = None) -> bool:
        """Check if cache entry is still valid"""
        try:
            if ttl is None:
                ttl = cache_entry.get('ttl', self.default_ttl)
            
            timestamp = cache_entry.get('timestamp', 0)
            return (time.time() - timestamp) < ttl
            
        except:
            return False
    
    def _get_cache_file_path(self, key: str) -> str:
        """Get file path for cache key"""
        # Sanitize key for filename
        safe_key = "".join(c for c in key if c.isalnum() or c in ('_', '-'))
        return os.path.join(self.cache_dir, f"{safe_key}.json")
    
    def cached_call(self, key: str, func, *args, ttl: Optional[int] = None, **kwargs):
        """
        Decorator-like function for caching function calls
        
        Args:
            key: Cache key
            func: Function to call
            *args: Function arguments
            ttl: Cache TTL
            **kwargs: Function keyword arguments
            
        Returns:
            Cached result or fresh function call result
        """
        try:
            # Check cache first
            cached_result = self.get(key, ttl)
            if cached_result is not None:
                return cached_result
            
            # Call function and cache result
            result = func(*args, **kwargs)
            self.set(key, result, ttl)
            
            return result
            
        except Exception as e:
            print(f"Cached call error for key {key}: {e}")
            # Fallback to direct function call
            return func(*args, **kwargs)
