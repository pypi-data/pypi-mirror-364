from .config import DomainConfiguration
from typing import List, Any, Optional
import numpy as np
import logging

logger = logging.getLogger("research_analyzer.embedding")

class EmbeddingGenerator:
    """
    Embedding generator supporting sentence-transformers, TF-IDF, and custom models.
    Automatically selects model based on configuration and data.
    """
    def __init__(self, config: DomainConfiguration):
        self.config = config
        self.model_name = config.embedding_model
        self.method = "auto"
        self._model = None
        self._cache = {}
        self._initialize_model()

    def _initialize_model(self):
        # Try to use sentence-transformers if available
        try:
            from sentence_transformers import SentenceTransformer
            if self.model_name == "auto":
                self.model_name = "sentence-transformers/all-MiniLM-L6-v2"
            self._model = SentenceTransformer(self.model_name)
            self.method = "sentence-transformers"
            logger.info(f"Loaded sentence-transformers model: {self.model_name}")
        except ImportError:
            logger.warning("sentence-transformers not available, falling back to TF-IDF.")
            self._model = None
            self.method = "tfidf"
        except Exception as e:
            logger.warning(f"Could not load embedding model: {e}. Falling back to TF-IDF.")
            self._model = None
            self.method = "tfidf"

    def generate_embeddings(self, documents: List[str]) -> Any:
        key = tuple(documents)
        if key in self._cache:
            return self._cache[key]
        if self.method == "sentence-transformers" and self._model is not None:
            embeddings = self._model.encode(documents, show_progress_bar=False)
        else:
            # Fallback: TF-IDF
            from sklearn.feature_extraction.text import TfidfVectorizer
            vectorizer = TfidfVectorizer(max_features=384)
            embeddings = vectorizer.fit_transform(documents).toarray()
        self._cache[key] = embeddings
        return embeddings 