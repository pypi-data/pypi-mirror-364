"""Utils module."""

import logging
from asyncio import get_event_loop

from langchain.globals import set_llm_cache

from thinkcache.config import (
    DEFAULT_DATABASE_PATH,
    DEFAULT_FAISS_INDEX_PATH,
    DEFAULT_SIMILARITY_THRESHOLD,
    ENABLE_QUANTIZATION,
)

# ---------------------------------------------------------------------------- #
#                               Logging Configuration                          #
# ---------------------------------------------------------------------------- #
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
common_logger = logging.getLogger(__name__)


# Helper functions for consistent logging
def log_info(message: str):
    """Log Info method."""
    common_logger.info(message)


def log_error(message: str, exc_info=False):
    """Log Error method."""
    common_logger.error(message, exc_info=exc_info)


# ---------------------------------------------------------------------------- #
#                             Semantic Cache Setup                             #
# ---------------------------------------------------------------------------- #
_semantic_cache_instance = None


def ensure_semantic_cache(**kwargs):
    """Ensure semantic cache is initialized globally with optional configuration.
    
    Args:
        **kwargs: Optional configuration parameters to override defaults:
            - database_path: Path to SQLite database
            - faiss_index_path: Path to FAISS index directory
            - similarity_threshold: Similarity threshold for semantic matching lower is better
            - max_cache_size: Maximum number of entries in cache
            - memory_cache_size: Size of in-memory cache
            - batch_size: Batch size for operations
            - enable_quantization: Whether to enable FAISS quantization
    
    Returns:
        SemanticCache: The global cache instance
    """
    global _semantic_cache_instance
    if _semantic_cache_instance is None:
        from thinkcache.cache import SemanticCache
        from thinkcache.config import (
            DEFAULT_DATABASE_PATH,
            DEFAULT_FAISS_INDEX_PATH,
            DEFAULT_SIMILARITY_THRESHOLD,
            DEFAULT_MAX_CACHE_SIZE,
            DEFAULT_MEMORY_CACHE_SIZE,
            DEFAULT_BATCH_SIZE,
            ENABLE_QUANTIZATION,
        )

        # Merge user config with defaults
        config = {
            "database_path": DEFAULT_DATABASE_PATH,
            "faiss_index_path": DEFAULT_FAISS_INDEX_PATH,
            "similarity_threshold": DEFAULT_SIMILARITY_THRESHOLD,
            "max_cache_size": DEFAULT_MAX_CACHE_SIZE,
            "memory_cache_size": DEFAULT_MEMORY_CACHE_SIZE,
            "batch_size": DEFAULT_BATCH_SIZE,
            "enable_quantization": ENABLE_QUANTIZATION,
        }
        config.update(kwargs)

        _semantic_cache_instance = SemanticCache(**config)
        set_llm_cache(_semantic_cache_instance)
        log_info("Semantic cache initialized and set globally.")
    return _semantic_cache_instance


def configure_semantic_cache(**kwargs):
    """Configure semantic cache before initialization.
    
    This function allows setting cache configuration before the first call
    to ensure_semantic_cache(). If cache is already initialized, raises ValueError.
    
    Args:
        **kwargs: Configuration parameters (same as ensure_semantic_cache)
        
    Raises:
        ValueError: If cache is already initialized
    """
    global _semantic_cache_instance
    if _semantic_cache_instance is not None:
        raise ValueError("Semantic cache is already initialized. Cannot reconfigure.")
    
    return ensure_semantic_cache(**kwargs)


def get_semantic_cache():
    """Get the current semantic cache instance.
    
    Returns:
        SemanticCache or None: Current cache instance, or None if not initialized
    """
    return _semantic_cache_instance


def reset_semantic_cache():
    """Reset the global semantic cache instance.
    
    This clears the current cache and allows for reconfiguration.
    """
    global _semantic_cache_instance
    if _semantic_cache_instance is not None:
        _semantic_cache_instance.clear_cache()
        _semantic_cache_instance = None
        log_info("Semantic cache reset.")
# ---------------s------------------------------------------------------------- #
#                              Asynchronous operations                         #
# ---------------------------------------------------------------------------- #


async def run_in_executor(func, *args, **kwargs):
    return await get_event_loop().run_in_executor(None, func, *args, **kwargs)
