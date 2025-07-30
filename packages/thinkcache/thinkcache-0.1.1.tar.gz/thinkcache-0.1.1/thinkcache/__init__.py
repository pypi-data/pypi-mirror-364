__version__ = "0.1.1"

def __getattr__(name: str):
    if name == "SemanticCache":
        from .cache import SemanticCache
        return SemanticCache
    elif name == "ensure_semantic_cache":
        from .utils import ensure_semantic_cache
        return ensure_semantic_cache
    elif name == "configure_semantic_cache":
        from .utils import configure_semantic_cache
        return configure_semantic_cache
    elif name == "get_semantic_cache":
        from .utils import get_semantic_cache
        return get_semantic_cache
    elif name == "reset_semantic_cache":
        from .utils import reset_semantic_cache
        return reset_semantic_cache
    elif name == "log_info":
        from .utils import log_info
        return log_info
    elif name == "log_error":
        from .utils import log_error
        return log_error
    raise AttributeError(f"module {__name__} has no attribute {name}")

__all__ = [
    "SemanticCache", 
    "ensure_semantic_cache", 
    "configure_semantic_cache",
    "get_semantic_cache",
    "reset_semantic_cache",
    "log_info", 
    "log_error"
]