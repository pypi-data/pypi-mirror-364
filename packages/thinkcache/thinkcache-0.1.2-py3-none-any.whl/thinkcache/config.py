# config.py
"""Config module."""

import os

# ---------------------------------------------------------------------------- #
#                                 Model Names                                  #
# ---------------------------------------------------------------------------- #

EMBEDDING_MODEL_NAME = "thenlper/gte-base"

# ---------------------------------------------------------------------------- #
#                                  API Keys/Bases                              #
# ---------------------------------------------------------------------------- #

OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


# ---------------------------------------------------------------------------- #
#                             Semantic Cache Configuration                     #
# ---------------------------------------------------------------------------- #

DUMMY_DOC_CONTENT = "Langchain Document Initializer"
DEFAULT_DATABASE_PATH = ".langchain.db"
# This is specifically for the SQLiteCache's FAISS index
DEFAULT_FAISS_INDEX_PATH = "semantic_faiss"

DEFAULT_SIMILARITY_THRESHOLD = 0.15
DEFAULT_MAX_CACHE_SIZE = 1000           # FAISS vector store size
DEFAULT_MEMORY_CACHE_SIZE = 100         # Response cache size
DEFAULT_EMBEDDING_CACHE_SIZE = 500      # Embedding cache size (NEW)
DEFAULT_BATCH_SIZE = 10
ENABLE_QUANTIZATION = False

