import logging
from typing import List, Dict, Set, Pattern, Optional, Callable
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import spacy
from .config import DomainConfiguration

logger = logging.getLogger("research_analyzer.preprocessing")

class DomainPreprocessor:
    """
    Advanced preprocessing system with domain-specific customization capabilities.
    Handles text cleaning, tokenization, normalization, and domain-specific transformations.
    """
    def __init__(self, config: DomainConfiguration):
        self.config = config
        self.lemmatizer = WordNetLemmatizer()
        self.nlp = None
        self.stats = {
            "documents_processed": 0,
            "total_tokens_before": 0,
            "total_tokens_after": 0,
            "custom_patterns_applied": 0
        }
        self._vocabulary: Set[str] = set()
        self._initialize_nlp_models()
        self._compile_patterns()

    def _initialize_nlp_models(self) -> None:
        try:
            model_name = self.config.preprocessing_rules.get("spacy_model", "en_core_web_sm")
            self.nlp = spacy.load(model_name)
            logger.info(f"Loaded spaCy model: {model_name}")
        except OSError:
            logger.warning("spaCy model not found. Using basic preprocessing only.")
            self.nlp = None

    def _compile_patterns(self) -> None:
        self.compiled_patterns = []
        default_patterns = [
            (r'\b\w{1,2}\b', ''),
            (r'\d+', 'NUMBER'),
            (r'[^\w\s]', ' '),
            (r'\s+', ' ')
        ]
        custom_patterns = self.config.technical_patterns
        all_patterns = default_patterns + [(pattern, '') for pattern in custom_patterns]
        for pattern, replacement in all_patterns:
            try:
                compiled_pattern = re.compile(pattern, re.IGNORECASE)
                self.compiled_patterns.append((compiled_pattern, replacement))
            except re.error as e:
                logger.warning(f"Invalid regex pattern '{pattern}': {e}")

    def process_documents(self, documents: List[str]) -> List[str]:
        processed_docs = []
        self._vocabulary.clear()
        for doc in documents:
            processed_doc = self.process_single_document(doc)
            processed_docs.append(processed_doc)
            self.stats["documents_processed"] += 1
        return processed_docs

    def process_single_document(self, document: str) -> str:
        original_tokens = len(document.split())
        self.stats["total_tokens_before"] += original_tokens
        text = self._basic_cleaning(document)
        text = self._apply_custom_patterns(text)
        text = self._tokenize_and_normalize(text)
        text = self._remove_stopwords(text)
        text = self._apply_domain_transformations(text)
        final_tokens = len(text.split())
        self.stats["total_tokens_after"] += final_tokens
        # Update vocabulary
        self._vocabulary.update(text.split())
        return text

    def _basic_cleaning(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text

    def _apply_custom_patterns(self, text: str) -> str:
        for pattern, replacement in self.compiled_patterns:
            text = pattern.sub(replacement, text)
            self.stats["custom_patterns_applied"] += 1
        return text

    def _tokenize_and_normalize(self, text: str) -> str:
        if self.nlp is not None:
            doc = self.nlp(text)
            tokens = []
            for token in doc:
                if token.is_punct or token.is_space:
                    continue
                normalized_token = token.lemma_.lower()
                if self._should_keep_token(normalized_token):
                    tokens.append(normalized_token)
            return ' '.join(tokens)
        else:
            tokens = word_tokenize(text)
            normalized_tokens = []
            for token in tokens:
                if token.isalpha():
                    lemmatized = self.lemmatizer.lemmatize(token.lower())
                    if self._should_keep_token(lemmatized):
                        normalized_tokens.append(lemmatized)
            return ' '.join(normalized_tokens)

    def _should_keep_token(self, token: str) -> bool:
        min_length = self.config.preprocessing_rules.get("min_token_length", 2)
        if len(token) < min_length:
            return False
        if token in self.config.custom_stopwords:
            return False
        exclusion_patterns = self.config.preprocessing_rules.get("exclusion_patterns", [])
        for pattern in exclusion_patterns:
            if re.match(pattern, token):
                return False
        return True

    def _remove_stopwords(self, text: str) -> str:
        try:
            english_stopwords = set(stopwords.words('english'))
        except LookupError:
            nltk.download('stopwords')
            english_stopwords = set(stopwords.words('english'))
        all_stopwords = english_stopwords.union(self.config.custom_stopwords)
        tokens = text.split()
        filtered_tokens = [token for token in tokens if token not in all_stopwords]
        return ' '.join(filtered_tokens)

    def _apply_domain_transformations(self, text: str) -> str:
        for term, synonyms in self.config.synonyms.items():
            for synonym in synonyms:
                text = re.sub(r'\b' + re.escape(synonym) + r'\b', term, text, flags=re.IGNORECASE)
        domain_transforms = self.config.preprocessing_rules.get("domain_transforms", {})
        for pattern, replacement in domain_transforms.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text

    def get_vocabulary(self) -> Set[str]:
        return set(self._vocabulary)

    def get_stats(self) -> Dict[str, int]:
        return self.stats.copy()

    def validate_preprocessing_rules(self) -> Dict[str, List[str]]:
        validation_results = {"errors": [], "warnings": [], "suggestions": []}
        for pattern in self.config.technical_patterns:
            try:
                re.compile(pattern)
            except re.error as e:
                validation_results["errors"].append(f"Invalid regex pattern '{pattern}': {e}")
        if not self.config.custom_stopwords:
            validation_results["suggestions"].append("Consider adding domain-specific stopwords")
        return validation_results 