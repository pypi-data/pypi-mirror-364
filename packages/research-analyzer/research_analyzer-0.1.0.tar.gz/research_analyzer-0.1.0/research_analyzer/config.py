from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field, asdict
from pathlib import Path
import json
import yaml
from enum import Enum

class ResearchDomain(Enum):
    CUSTOM = "custom"
    PSYCHOLOGY = "psychology"
    BIOLOGY = "biology"
    # Extend as needed

@dataclass
class DomainConfiguration:
    domain_name: str = ""
    research_field: ResearchDomain = ResearchDomain.CUSTOM
    subfields: List[str] = field(default_factory=list)
    data_types: List[str] = field(default_factory=list)
    research_objectives: List[str] = field(default_factory=list)
    key_terms: Dict[str, str] = field(default_factory=dict)
    synonyms: Dict[str, List[str]] = field(default_factory=dict)
    hierarchies: Dict[str, List[str]] = field(default_factory=dict)
    custom_stopwords: set = field(default_factory=set)
    technical_patterns: List[str] = field(default_factory=list)
    embedding_model: str = "auto"
    topic_modeling_method: str = "bertopic"
    min_topic_size: int = 10
    network_types: List[str] = field(default_factory=lambda: ["cooccurrence"])
    visualization_style: str = "academic"
    custom_domains: Dict[str, List[str]] = field(default_factory=dict)
    custom_metrics: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    preprocessing_rules: Dict[str, Any] = field(default_factory=dict)
    output_preferences: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> Dict[str, List[str]]:
        validation_results = {"errors": [], "warnings": [], "suggestions": []}
        if not self.domain_name:
            validation_results["errors"].append("Domain name is required")
        if not self.research_objectives:
            validation_results["warnings"].append("No research objectives specified")
        for domain_name, keywords in self.custom_domains.items():
            if len(keywords) < 2:
                validation_results["suggestions"].append(
                    f"Domain '{domain_name}' has few keywords - consider adding more"
                )
        if not self.key_terms:
            validation_results["warnings"].append("No key terms defined")
        return validation_results

    def save(self, filepath: Union[str, Path]) -> None:
        filepath = Path(filepath)
        config_dict = self.to_dict()
        if filepath.suffix.lower() == '.json':
            with open(filepath, 'w') as f:
                json.dump(config_dict, f, indent=2, default=str)
        elif filepath.suffix.lower() in ['.yml', '.yaml']:
            with open(filepath, 'w') as f:
                yaml.dump(config_dict, f, default_flow_style=False)
        else:
            raise ValueError("Unsupported file format. Use .json, .yml, or .yaml")

    @classmethod
    def load(cls, filepath: Union[str, Path]) -> 'DomainConfiguration':
        filepath = Path(filepath)
        if filepath.suffix.lower() == '.json':
            with open(filepath, 'r') as f:
                config_dict = json.load(f)
        elif filepath.suffix.lower() in ['.yml', '.yaml']:
            with open(filepath, 'r') as f:
                config_dict = yaml.safe_load(f)
        else:
            raise ValueError("Unsupported file format. Use .json, .yml, or .yaml")
        return cls.from_dict(config_dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # Convert enums to their value
        d['research_field'] = self.research_field.value if isinstance(self.research_field, Enum) else self.research_field
        # Convert set to list for serialization
        d['custom_stopwords'] = list(self.custom_stopwords)
        return d

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'DomainConfiguration':
        # Convert research_field back to enum
        if 'research_field' in config_dict and not isinstance(config_dict['research_field'], ResearchDomain):
            config_dict['research_field'] = ResearchDomain(config_dict['research_field'])
        # Convert custom_stopwords back to set
        if 'custom_stopwords' in config_dict and not isinstance(config_dict['custom_stopwords'], set):
            config_dict['custom_stopwords'] = set(config_dict['custom_stopwords'])
        return cls(**config_dict)

class ConfigurationManager:
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path.home() / ".research_analyzer"
        self.config_dir.mkdir(exist_ok=True)
        self.templates_dir = self.config_dir / "templates"
        self.templates_dir.mkdir(exist_ok=True)

    def create_template(self, domain: ResearchDomain) -> DomainConfiguration:
        config = DomainConfiguration()
        config.research_field = domain
        if domain == ResearchDomain.PSYCHOLOGY:
            config.domain_name = "Psychology Research"
            config.subfields = ["cognitive", "behavioral", "social", "clinical"]
            config.data_types = ["interviews", "surveys", "case_studies", "observations"]
            config.key_terms = {
                "behavior": "Observable actions and responses",
                "cognition": "Mental processes including thinking and perception",
                "emotion": "Psychological and physiological states"
            }
            config.custom_domains = {
                "Stress Response": ["stress", "anxiety", "cortisol", "pressure"],
                "Social Interaction": ["communication", "group", "social", "interaction"],
                "Learning": ["memory", "recall", "learning", "retention"]
            }
        elif domain == ResearchDomain.BIOLOGY:
            config.domain_name = "Biology Research"
            config.subfields = ["molecular", "cellular", "ecology", "genetics"]
            config.data_types = ["research_papers", "lab_reports", "field_notes"]
            config.key_terms = {
                "gene": "Unit of heredity",
                "protein": "Large biomolecule",
                "ecosystem": "Biological community and environment"
            }
            config.custom_domains = {
                "Gene Expression": ["expression", "transcription", "mrna", "protein"],
                "Cell Division": ["mitosis", "meiosis", "chromosome", "division"],
                "Evolution": ["selection", "adaptation", "fitness", "mutation"]
            }
        return config

    def list_templates(self) -> List[str]:
        return [domain.value for domain in ResearchDomain if domain != ResearchDomain.CUSTOM]

    def save_user_config(self, config: DomainConfiguration, name: str) -> None:
        filepath = self.config_dir / f"{name}.json"
        config.save(filepath)

    def load_user_config(self, name: str) -> DomainConfiguration:
        filepath = self.config_dir / f"{name}.json"
        return DomainConfiguration.load(filepath)

    def list_user_configs(self) -> List[str]:
        return [f.stem for f in self.config_dir.glob("*.json")] 