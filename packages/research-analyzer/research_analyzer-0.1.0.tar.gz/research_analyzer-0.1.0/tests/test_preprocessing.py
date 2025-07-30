import pytest
from research_analyzer.config import DomainConfiguration
from research_analyzer.preprocessing import DomainPreprocessor

@pytest.fixture
def config():
    cfg = DomainConfiguration()
    cfg.custom_stopwords = {"the", "and"}
    cfg.synonyms = {"test": ["exam", "assessment"]}
    return cfg

@pytest.fixture
def preprocessor(config):
    return DomainPreprocessor(config)

def test_basic_cleaning(preprocessor):
    text = "  This is a TEST.  "
    cleaned = preprocessor._basic_cleaning(text)
    assert cleaned == "this is a test."

def test_stopword_removal(preprocessor):
    text = "this is the test and exam"
    no_stop = preprocessor._remove_stopwords(text)
    assert "the" not in no_stop and "and" not in no_stop

def test_synonym_replacement(preprocessor):
    text = "the exam was hard"
    replaced = preprocessor._apply_domain_transformations(text)
    assert "test" in replaced
    assert "exam" not in replaced

def test_vocabulary_extraction(preprocessor):
    docs = ["this is a test", "another test"]
    preprocessor.process_documents(docs)
    vocab = preprocessor.get_vocabulary()
    assert "test" in vocab
    assert "this" in vocab 