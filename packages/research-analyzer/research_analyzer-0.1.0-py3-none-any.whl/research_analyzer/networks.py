from .config import DomainConfiguration
from typing import List, Any, Dict
import logging
import numpy as np

logger = logging.getLogger("research_analyzer.networks")

class NetworkAnalyzer:
    """
    Handles construction and analysis of co-occurrence, similarity, and concept networks.
    Uses networkx for graph analysis.
    """
    def __init__(self, config: DomainConfiguration):
        self.config = config
        try:
            import networkx as nx
            self.nx = nx
        except ImportError:
            logger.warning("networkx not available. Network analysis will be limited.")
            self.nx = None

    def analyze_networks(self, documents: List[str], embeddings: Any, focus_terms: List[str]) -> Dict[str, Any]:
        results = {}
        if self.nx is not None:
            results["cooccurrence"] = self._build_cooccurrence_network(documents, focus_terms)
            results["similarity"] = self._build_similarity_network(embeddings)
            results["concept"] = self._build_concept_network(documents, focus_terms)
        else:
            results = {"cooccurrence": {}, "similarity": {}, "concept": {}}
        return results

    def _build_cooccurrence_network(self, documents: List[str], focus_terms: List[str]) -> Dict[str, Any]:
        G = self.nx.Graph()
        for doc in documents:
            tokens = set(doc.split())
            for t1 in tokens:
                for t2 in tokens:
                    if t1 != t2:
                        G.add_edge(t1, t2)
        centrality = self.nx.degree_centrality(G)
        return {"graph": G, "centrality": centrality}

    def _build_similarity_network(self, embeddings: Any) -> Dict[str, Any]:
        G = self.nx.Graph()
        if isinstance(embeddings, np.ndarray):
            n = embeddings.shape[0]
            for i in range(n):
                for j in range(i+1, n):
                    sim = float(np.dot(embeddings[i], embeddings[j]) / (np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j]) + 1e-8))
                    if sim > 0.8:
                        G.add_edge(i, j, weight=sim)
        return {"graph": G}

    def _build_concept_network(self, documents: List[str], focus_terms: List[str]) -> Dict[str, Any]:
        G = self.nx.Graph()
        for doc in documents:
            tokens = set(doc.split())
            for term in focus_terms:
                if term in tokens:
                    for t in tokens:
                        if t != term:
                            G.add_edge(term, t)
        return {"graph": G} 