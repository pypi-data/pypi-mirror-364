import pytest
from research_analyzer.config import DomainConfiguration, ConfigurationManager, ResearchDomain

def test_validation():
    config = DomainConfiguration()
    result = config.validate()
    assert "errors" in result
    assert any("Domain name is required" in e for e in result["errors"])

def test_serialization(tmp_path):
    config = DomainConfiguration(domain_name="TestDomain", research_objectives=["obj"])
    path = tmp_path / "config.json"
    config.save(path)
    loaded = DomainConfiguration.load(path)
    assert loaded.domain_name == "TestDomain"
    assert loaded.research_objectives == ["obj"]

def test_template_creation():
    cm = ConfigurationManager()
    config = cm.create_template(ResearchDomain.PSYCHOLOGY)
    assert config.domain_name == "Psychology Research"
    assert "behavior" in config.key_terms 