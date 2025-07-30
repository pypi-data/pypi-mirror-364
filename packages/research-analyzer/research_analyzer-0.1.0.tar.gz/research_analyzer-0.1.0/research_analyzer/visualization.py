from .config import DomainConfiguration
from typing import Any, Dict
import logging

logger = logging.getLogger("research_analyzer.visualization")

class Visualizer:
    """
    Generates static and interactive visualizations for analysis results.
    Supports matplotlib, seaborn, and plotly if available.
    """
    def __init__(self, config: DomainConfiguration):
        self.config = config

    def visualize(self, results: Any) -> None:
        logger.info("Visualization not implemented. Use create_topic_network, create_metrics_dashboard, etc.")

    def create_topic_network(self, topic_results: Dict[str, Any]) -> Any:
        try:
            import networkx as nx
            import matplotlib.pyplot as plt
            G = nx.Graph()
            # Example: add nodes/edges from topic info
            for topic in topic_results.get("topic_info", []):
                G.add_node(topic.get("Name", "Topic"))
            nx.draw(G, with_labels=True)
            plt.title("Topic Network")
            plt.show()
            return plt.gcf()
        except ImportError:
            logger.warning("matplotlib or networkx not available.")
            return None

    def create_metrics_dashboard(self, metrics: Dict[str, Any]) -> Any:
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns
            import pandas as pd
            df = pd.DataFrame(metrics).T
            df.plot(kind="bar")
            plt.title("Metrics Dashboard")
            plt.tight_layout()
            plt.show()
            return plt.gcf()
        except ImportError:
            logger.warning("matplotlib, seaborn, or pandas not available.")
            return None 