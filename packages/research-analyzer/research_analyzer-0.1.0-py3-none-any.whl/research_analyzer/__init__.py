"""
research_analyzer: Universal, domain-agnostic research analysis toolkit for extracting insights from textual datasets.
"""
__version__ = "0.1.0"

# Expose main classes for convenience imports
from .config import DomainConfiguration, ConfigurationManager, ResearchDomain
from .analysis import ResearchAnalyzer

__all__ = [
    "__version__",
    "DomainConfiguration",
    "ConfigurationManager",
    "ResearchDomain",
    "ResearchAnalyzer"
] 