# Smart Semantic Cache

A high-performance, multi-layered semantic caching system that dramatically reduces LLM costs and latency through intelligent similarity-based response caching.

## Why Semantic Cache?

Traditional caching requires **exact** query matches. Semantic caching understands that "What's the capital of France?" and "Tell me France's capital city" should return the same cached result. This can reduce your LLM API costs by 60–90% in real applications.

## Key Features

* **Multi-Layer Intelligence**: Memory cache → SQLite → FAISS vector similarity
* **Lightning Fast**: Sub-millisecond memory lookups, <10ms semantic search
* **Configurable Similarity**: Fine-tune cache hit sensitivity (0.0–1.0)
* **Memory Efficient**: Optional FAISS quantization for large-scale deployments
* **Async Ready**: Full async support for high-throughput applications
* **Rich Metrics**: Comprehensive performance monitoring and analytics
* **Smart Eviction**: LRU-based cache management with intelligent cleanup
* **Production Ready**: Thread-safe, error-resilient, battle-tested

## Installation

```bash
pip install thinkcache
```

### Optional Dependencies

```bash
# For GPU acceleration (recommended for production)
pip install thinkcache[quantization]

# For development and testing
pip install thinkcache[dev]
```

## Quick Start

### Method 1: Global Cache Setup (Recommended)

```python
from thinkcache import ensure_semantic_cache
from langchain_openai import OpenAI

# Initialize semantic cache globally - one line setup!
ensure_semantic_cache(
    similarity_threshold=0.15,
    max_cache_size=1000
)

llm = OpenAI(temperature=0)

response1 = llm.invoke("What is the capital of France?")
response2 = llm.invoke("Tell me the capital city of France")
response3 = llm.invoke("France's capital is?")
```

### Method 2: Direct Cache Usage

```python
from thinkcache import SemanticCache
from langchain.globals import set_llm_cache

cache = SemanticCache(
    database_path="./production_cache.db",
    faiss_index_path="./vector_cache",
    similarity_threshold=0.15,
    max_cache_size=5000,
    memory_cache_size=1000,
    enable_quantization=True
)

set_llm_cache(cache)
```

## Configuration Methods

### Global Configuration (Before First Use)

```python
from thinkcache import configure_semantic_cache

configure_semantic_cache(
    database_path="./my_cache.db",
    similarity_threshold=0.15,
    max_cache_size=2000
)

from thinkcache import ensure_semantic_cache
ensure_semantic_cache()
```

### Runtime Configuration

```python
from thinkcache import ensure_semantic_cache

cache = ensure_semantic_cache(
    similarity_threshold=0.2,
    database_path="./cache.db",
    faiss_index_path="./vectors",
    max_cache_size=1000,
    memory_cache_size=500,
    batch_size=20,
    enable_quantization=False
)
```

### Production Configuration

```python
from thinkcache import configure_semantic_cache

configure_semantic_cache(
    database_path="/var/cache/semantic/cache.db",
    faiss_index_path="/var/cache/semantic/vectors",
    similarity_threshold=0.15,
    max_cache_size=10000,
    memory_cache_size=2000,
    enable_quantization=True,
    batch_size=50
)
```

## Cache Management

### Getting Cache Instance

```python
from thinkcache import get_semantic_cache

cache = get_semantic_cache()

if cache:
    print("Cache is active and ready!")
else:
    print("No cache initialized yet")
```

### Resetting Cache

```python
from thinkcache import reset_semantic_cache

reset_semantic_cache()

from thinkcache import configure_semantic_cache
configure_semantic_cache(similarity_threshold=0.1)
```

### Handling Already Initialized Cache

```python
from thinkcache import configure_semantic_cache

try:
    configure_semantic_cache(similarity_threshold=0.1)
except ValueError as e:
    print("Cache already initialized!")
    from thinkcache import reset_semantic_cache
    reset_semantic_cache()
    configure_semantic_cache(similarity_threshold=0.1)
```

## Performance Monitoring

### Real-time Metrics

```python
from thinkcache import get_semantic_cache

cache = get_semantic_cache()

if cache:
    metrics = cache.get_metrics()

    print(f"Cache Hit Rate: {metrics['hit_rate']:.1%}")
    print(f"Total Requests: {metrics['total_requests']:,}")
    print(f"Memory Hits: {metrics['memory_hits']:,}")
    print(f"Semantic Hits: {metrics['semantic_hits']:,}")
    print(f"Avg Embedding Time: {metrics['avg_embedding_time']:.3f}s")
    print(f"Avg Search Time: {metrics['avg_search_time']:.3f}s")
```

### Cache Cleanup

```python
from thinkcache import get_semantic_cache

cache = get_semantic_cache()
if cache:
    cache.clear_cache()
    print("All caches cleared!")
```

## Architecture Overview

```
Query → Memory Cache → SQLite Cache → Semantic Search → LLM API
  ↓         ↓             ↓              ↓            ↓
 <1ms    ~1-2ms        ~2-5ms        ~5-15ms      100-2000ms
```

### How It Works

1. **Memory Cache**: Lightning-fast LRU cache for recently accessed queries
2. **SQLite Cache**: Persistent exact-match cache with indexing
3. **Semantic Search**: FAISS-powered vector similarity search
4. **Embedding Cache**: Cached embeddings to avoid recomputation
5. **Smart Eviction**: Automatic cleanup based on usage patterns

## Advanced Usage

### Async Operations

```python
import asyncio
from thinkcache import ensure_semantic_cache
from langchain_openai import OpenAI

ensure_semantic_cache()

async def cached_queries():
    llm = OpenAI()
    tasks = [
        llm.ainvoke("Explain quantum computing"),
        llm.ainvoke("What is quantum computing?"),
        llm.ainvoke("Define quantum computing")
    ]
    results = await asyncio.gather(*tasks)
    return results

results = asyncio.run(cached_queries())
```

### Custom Similarity Thresholds

```python
from thinkcache import configure_semantic_cache

configure_semantic_cache(similarity_threshold=0.1)
configure_semantic_cache(similarity_threshold=0.4)
configure_semantic_cache(similarity_threshold=0.2)
```

### Multiple Cache Instances

```python
from thinkcache import SemanticCache

qa_cache = SemanticCache(
    database_path="./qa_cache.db",
    similarity_threshold=0.15
)

summarization_cache = SemanticCache(
    database_path="./summary_cache.db",
    similarity_threshold=0.25
)
```

## Complete Workflow Example

```python
from thinkcache import (
    configure_semantic_cache,
    ensure_semantic_cache,
    get_semantic_cache,
    reset_semantic_cache
)
from langchain_openai import OpenAI

configure_semantic_cache(
    similarity_threshold=0.2,
    max_cache_size=5000,
    enable_quantization=True
)

cache = ensure_semantic_cache()

llm = OpenAI(temperature=0)
response = llm.invoke("What is machine learning?")

metrics = cache.get_metrics()
print(f"Hit rate: {metrics['hit_rate']:.1%}")

reset_semantic_cache()

configure_semantic_cache(similarity_threshold=0.1)
```

## Configuration Reference

| Parameter              | Default                  | Description                              |
| ---------------------- | ------------------------ | ---------------------------------------- |
| `database_path`        | `.langchain.db`          | SQLite database file path                |
| `faiss_index_path`     | `./semantic_cache_index` | FAISS vector index directory             |
| `similarity_threshold` | `0.5`                    | Semantic similarity threshold (0.0–1.0)  |
| `max_cache_size`       | `1000`                   | Maximum entries in vector store          |
| `memory_cache_size`    | `100`                    | Maximum entries in memory cache          |
| `batch_size`           | `10`                     | Batch size for vector operations         |
| `enable_quantization`  | `False`                  | Enable FAISS quantization for efficiency |

## Troubleshooting

**Cache not working?**

```python
from thinkcache import get_semantic_cache
cache = get_semantic_cache()
print(f"Cache active: {cache is not None}")
```

**Configuration errors?**

```python
from thinkcache import reset_semantic_cache, configure_semantic_cache
reset_semantic_cache()
configure_semantic_cache(similarity_threshold=0.3)
```

**Low hit rates?**

```python
from thinkcache import reset_semantic_cache, configure_semantic_cache
reset_semantic_cache()
configure_semantic_cache(similarity_threshold=0.3)
```

**Memory issues?**

```python
from thinkcache import configure_semantic_cache
configure_semantic_cache(enable_quantization=True)
```

## Performance Tips

1. Start with 0.2 similarity threshold
2. Use `configure_semantic_cache()` for production
3. Enable quantization for large caches
4. Use a larger memory cache in production
5. Monitor hit rates and adjust threshold
6. Reset cache regularly during development

## Requirements

* Python 3.8+
* Core: FAISS, HuggingFace Transformers, SQLite
* Optional: faiss-gpu (for GPU acceleration)

## License

MIT License – see [LICENSE](LICENSE) file for details.

## Changelog

### v0.1.1

* Multi-layer caching system
* FAISS integration with quantization
* Comprehensive metrics and monitoring
* Full async support
