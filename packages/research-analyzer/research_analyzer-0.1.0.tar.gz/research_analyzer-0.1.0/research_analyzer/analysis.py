from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import pandas as pd
import numpy as np
from .config import DomainConfiguration

class ResearchAnalyzer:
    def __init__(self, config: DomainConfiguration):
        self.config = config
        self.preprocessor = None
        self.embedder = None
        self.topic_modeler = None
        self.network_analyzer = None
        self.metrics_extractor = None
        self.visualizer = None
        self._initialize_components()

    def _initialize_components(self) -> None:
        from .preprocessing import DomainPreprocessor
        from .embedding import EmbeddingGenerator
        from .topics import TopicModeler
        from .networks import NetworkAnalyzer
        from .metrics import MetricsExtractor
        from .visualization import Visualizer
        self.preprocessor = DomainPreprocessor(self.config)
        self.embedder = EmbeddingGenerator(self.config)
        self.topic_modeler = TopicModeler(self.config)
        self.network_analyzer = NetworkAnalyzer(self.config)
        self.metrics_extractor = MetricsExtractor(self.config)
        self.visualizer = Visualizer(self.config)

    def analyze_documents(self, documents: List[str], filenames: Optional[List[str]] = None, analysis_types: Optional[List[str]] = None) -> Dict[str, Any]:
        if analysis_types is None:
            analysis_types = ["preprocessing", "topics", "networks", "metrics"]
        results = {
            "config": self.config.to_dict(),
            "document_count": len(documents),
            "analysis_timestamp": pd.Timestamp.now().isoformat()
        }
        if "preprocessing" in analysis_types:
            processed_docs = self.preprocessor.process_documents(documents)
            results["preprocessing"] = {
                "processed_documents": processed_docs,
                "preprocessing_stats": self.preprocessor.get_stats(),
                "vocabulary_size": len(self.preprocessor.get_vocabulary())
            }
        else:
            processed_docs = documents
        embeddings = self.embedder.generate_embeddings(processed_docs)
        results["embeddings"] = {
            "model_name": getattr(self.embedder, 'model_name', None),
            "embedding_dimensions": getattr(embeddings, 'shape', [None, None])[1] if hasattr(embeddings, 'shape') else None,
            "embedding_method": getattr(self.embedder, 'method', None)
        }
        if "topics" in analysis_types:
            topic_results = self.topic_modeler.fit_transform(
                processed_docs,
                embeddings,
                seed_keywords=self._extract_seed_keywords()
            )
            results["topics"] = topic_results
        if "networks" in analysis_types:
            network_results = self.network_analyzer.analyze_networks(
                processed_docs,
                embeddings,
                focus_terms=list(self.config.key_terms.keys())
            )
            results["networks"] = network_results
        if "metrics" in analysis_types:
            metrics_results = self.metrics_extractor.extract_all_metrics(
                processed_docs,
                embeddings,
                topic_model=results.get("topics", {}).get("model"),
                filenames=filenames
            )
            results["metrics"] = metrics_results
        return results

    def _extract_seed_keywords(self) -> List[str]:
        seed_keywords = list(self.config.key_terms.keys())
        for domain_keywords in self.config.custom_domains.values():
            seed_keywords.extend(domain_keywords)
        return list(set(seed_keywords))

    def quick_analysis(self, documents: List[str], research_question: str = "") -> Dict[str, Any]:
        self._auto_configure(documents, research_question)
        results = self.analyze_documents(documents)
        results["insights"] = self._generate_insights(results)
        results["recommendations"] = self._generate_recommendations(results)
        return results

    def _auto_configure(self, documents: List[str], research_question: str) -> None:
        doc_lengths = [len(doc.split()) for doc in documents]
        avg_length = np.mean(doc_lengths)
        if len(documents) < 50:
            self.config.min_topic_size = max(2, len(documents) // 10)
        elif len(documents) > 1000:
            self.config.min_topic_size = 20
        if avg_length > 500:
            self.config.embedding_model = "sentence-transformers/all-MiniLM-L12-v2"
        else:
            self.config.embedding_model = "sentence-transformers/all-MiniLM-L6-v2"

    def _generate_insights(self, results: Dict[str, Any]) -> List[str]:
        insights = []
        if "topics" in results:
            topic_count = len(results["topics"].get("topic_info", []))
            insights.append(f"Identified {topic_count} distinct topics in your data")
            if topic_count > len(results.get("preprocessing", {}).get("processed_documents", [])) * 0.3:
                insights.append("High topic diversity detected - consider increasing min_topic_size")
        if "metrics" in results:
            metrics_data = results["metrics"]
            high_prevalence_domains = [
                domain for domain, data in metrics_data.items()
                if data.get("prevalence", 0) > 0.1
            ]
            if high_prevalence_domains:
                insights.append(f"High prevalence detected in: {', '.join(high_prevalence_domains)}")
        return insights

    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        recommendations = []
        doc_count = results.get("document_count", 0)
        if doc_count < 20:
            recommendations.append("Consider adding more documents for more robust analysis")
        if "topics" in results:
            topic_coherence = results["topics"].get("coherence_score", 0)
            if topic_coherence < 0.4:
                recommendations.append("Low topic coherence - try adjusting preprocessing or topic parameters")
        return recommendations

    def export_results(self, results: Dict[str, Any], output_dir: Union[str, Path], formats: List[str] = None) -> Dict[str, Path]:
        if formats is None:
            formats = ["csv", "json", "html"]
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        exported_files = {}
        if "csv" in formats:
            csv_path = output_dir / "analysis_results.csv"
            self._export_to_csv(results, csv_path)
            exported_files["csv"] = csv_path
        if "json" in formats:
            json_path = output_dir / "analysis_results.json"
            self._export_to_json(results, json_path)
            exported_files["json"] = json_path
        if "html" in formats:
            html_path = output_dir / "analysis_report.html"
            self._export_to_html(results, html_path)
            exported_files["html"] = html_path
        return exported_files

    def _export_to_csv(self, results: Dict[str, Any], filepath: Path) -> None:
        pass

    def _export_to_json(self, results: Dict[str, Any], filepath: Path) -> None:
        pass

    def _export_to_html(self, results: Dict[str, Any], filepath: Path) -> None:
        pass 