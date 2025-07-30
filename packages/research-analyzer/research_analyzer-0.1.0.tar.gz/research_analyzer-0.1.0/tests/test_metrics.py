import pytest
from research_analyzer.config import DomainConfiguration
from research_analyzer.metrics import MetricsExtractor

def custom_metric(docs, **kwargs):
    return {"custom": sum("custom" in doc for doc in docs)}

def test_frequency_metrics():
    config = DomainConfiguration()
    config.custom_domains = {"DomainA": ["apple", "banana"]}
    docs = ["apple pie", "banana split", "no fruit"]
    me = MetricsExtractor(config)
    results = me.extract_all_metrics(docs, None)
    assert "DomainA" in results
    assert results["DomainA"]["count"] == 2

def test_custom_metric_plugin():
    config = DomainConfiguration()
    config.custom_metrics = {
        "my_metric": {"function": custom_metric, "parameters": {}}
    }
    docs = ["custom metric", "no match"]
    me = MetricsExtractor(config)
    results = me.extract_all_metrics(docs, None)
    assert "my_metric" in results
    assert results["my_metric"]["custom"] == 1 