from .config import DomainConfiguration
from typing import List, Any, Dict, Optional
import numpy as np
import logging

logger = logging.getLogger("research_analyzer.topics")

class TopicModeler:
    """
    Advanced topic modeling system with domain-specific guidance capabilities.
    Integrates BERTopic if available, with fallback to simple clustering.
    """
    def __init__(self, config: DomainConfiguration):
        self.config = config
        self.model = None
        self.topics = None
        self.probabilities = None
        self.topic_info = None
        self._bertopic_available = False
        self._initialize_model()

    def _initialize_model(self):
        try:
            from bertopic import BERTopic
            self._bertopic_available = True
        except ImportError:
            logger.warning("BERTopic not available. Using fallback topic modeling.")
            self._bertopic_available = False

    def fit_transform(self, documents: List[str], embeddings: Optional[Any] = None, seed_keywords: Optional[List[str]] = None) -> Dict[str, Any]:
        if self._bertopic_available:
            from bertopic import BERTopic
            try:
                model = BERTopic(min_topic_size=self.config.min_topic_size, verbose=False)
                topics, probs = model.fit_transform(documents, embeddings=embeddings)
                topic_info = model.get_topic_info().to_dict('records')
                self.model = model
                self.topics = topics
                self.probabilities = probs
                self.topic_info = topic_info
                coherence_score = self._calculate_coherence(documents, model)
                diversity_score = self._calculate_diversity(model)
                topic_count = len(set(topics)) - (1 if -1 in topics else 0)
                outlier_count = sum(1 for t in topics if t == -1)
                return {
                    "model": model,
                    "topics": topics,
                    "probabilities": probs,
                    "topic_info": topic_info,
                    "coherence_score": coherence_score,
                    "diversity_score": diversity_score,
                    "topic_count": topic_count,
                    "outlier_count": outlier_count,
                    "domain_alignment": {},
                    "topic_quality": {}
                }
            except Exception as e:
                logger.warning(f"BERTopic failed: {e}. Using fallback.")
        # Fallback: simple clustering (all docs to one topic)
        topics = [0 for _ in documents]
        return {
            "model": None,
            "topics": topics,
            "probabilities": [],
            "topic_info": [],
            "coherence_score": 0.0,
            "diversity_score": 0.0,
            "topic_count": 1,
            "outlier_count": 0,
            "domain_alignment": {},
            "topic_quality": {}
        }

    def _calculate_coherence(self, documents: List[str], model: Any) -> float:
        try:
            from gensim.models import CoherenceModel
            from gensim.corpora import Dictionary
            texts = [doc.split() for doc in documents]
            dictionary = Dictionary(texts)
            topics = []
            for topic_id in range(len(model.get_topics())):
                topic_words = [word for word, _ in model.get_topic(topic_id)]
                topics.append(topic_words)
            coherence_model = CoherenceModel(
                topics=topics,
                texts=texts,
                dictionary=dictionary,
                coherence='c_v'
            )
            return coherence_model.get_coherence()
        except Exception as e:
            logger.warning(f"Could not calculate coherence: {e}")
            return 0.0

    def _calculate_diversity(self, model: Any) -> float:
        try:
            all_words = set()
            topic_words = []
            for topic_id in range(len(model.get_topics())):
                words = [word for word, _ in model.get_topic(topic_id)]
                topic_words.append(set(words))
                all_words.update(words)
            if not all_words:
                return 0.0
            unique_words = len(all_words)
            total_words = sum(len(words) for words in topic_words)
            return unique_words / total_words if total_words > 0 else 0.0
        except Exception as e:
            logger.warning(f"Could not calculate diversity: {e}")
            return 0.0

    def refine_topics(self, merge_topics: Optional[List[Any]] = None, split_topics: Optional[List[Any]] = None) -> Dict[str, Any]:
        # Stub for topic refinement
        logger.info("Topic refinement not implemented in fallback mode.")
        return {"merges_performed": 0, "splits_performed": 0, "new_topic_count": 0} 