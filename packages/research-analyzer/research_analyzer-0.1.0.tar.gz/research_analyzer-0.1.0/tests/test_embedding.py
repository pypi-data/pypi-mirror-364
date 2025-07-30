import pytest
from research_analyzer.config import DomainConfiguration
from research_analyzer.embedding import EmbeddingGenerator
import numpy as np

def test_embedding_shape(monkeypatch):
    config = DomainConfiguration()
    config.embedding_model = "auto"
    eg = EmbeddingGenerator(config)
    docs = ["this is a test", "another test"]
    emb = eg.generate_embeddings(docs)
    assert isinstance(emb, np.ndarray)
    assert emb.shape[0] == 2

    # Test caching
    emb2 = eg.generate_embeddings(docs)
    assert np.allclose(emb, emb2)


def test_tfidf_fallback(monkeypatch):
    # Force TF-IDF fallback by monkeypatching _initialize_model
    config = DomainConfiguration()
    eg = EmbeddingGenerator(config)
    eg._model = None
    eg.method = "tfidf"
    docs = ["this is a test", "another test"]
    emb = eg.generate_embeddings(docs)
    assert isinstance(emb, np.ndarray)
    assert emb.shape[0] == 2 