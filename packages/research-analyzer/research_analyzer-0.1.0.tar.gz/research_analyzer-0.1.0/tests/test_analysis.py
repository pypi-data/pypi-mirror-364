import pytest
from research_analyzer.config import DomainConfiguration
from research_analyzer.analysis import ResearchAnalyzer

def test_full_analysis_pipeline():
    config = DomainConfiguration(domain_name="TestDomain", research_objectives=["obj"], key_terms={"test": "desc"})
    analyzer = ResearchAnalyzer(config)
    docs = ["this is a test document", "another test"]
    results = analyzer.analyze_documents(docs)
    assert "preprocessing" in results
    assert "embeddings" in results
    assert "topics" in results
    assert "networks" in results
    assert "metrics" in results
    assert results["document_count"] == 2 