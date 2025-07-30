from .config import DomainConfiguration
from typing import List, Any, Dict, Optional, Callable
import logging

logger = logging.getLogger("research_analyzer.metrics")

class MetricsExtractor:
    """
    Extracts frequency-based and custom metrics. Supports plugin system for user-defined metrics.
    """
    def __init__(self, config: DomainConfiguration):
        self.config = config

    def extract_all_metrics(self, documents: List[str], embeddings: Any, topic_model: Any = None, filenames: Optional[List[str]] = None) -> Dict[str, Any]:
        results = {}
        # Frequency-based metrics for custom domains
        for domain, keywords in self.config.custom_domains.items():
            count = sum(any(kw in doc for kw in keywords) for doc in documents)
            prevalence = count / len(documents) if documents else 0.0
            results[domain] = {"count": count, "prevalence": prevalence}
        # Custom metrics plugins
        for metric_name, metric_info in self.config.custom_metrics.items():
            func = metric_info.get("function")
            if callable(func):
                try:
                    results[metric_name] = func(documents, **metric_info.get("parameters", {}))
                except Exception as e:
                    logger.warning(f"Custom metric '{metric_name}' failed: {e}")
        return results 