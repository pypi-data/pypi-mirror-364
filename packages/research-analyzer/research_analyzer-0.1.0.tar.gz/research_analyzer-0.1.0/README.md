# research_analyzer

Universal, domain-agnostic research analysis toolkit for extracting insights from textual datasets.

## Overview

`research_analyzer` is a modular, extensible Python library designed for researchers and simulation teams across disciplines. It enables extraction of meaningful insights and metrics from textual datasets, supporting custom research domains, terminology, and analysis workflows.

## Features
- Dynamic configuration system for any research domain
- Modular architecture: preprocessing, embedding, topic modeling, networks, metrics, visualization
- High-level and low-level APIs for flexible use
- Extensible with custom metrics and domain definitions

## Installation
```bash
pip install -r requirements.txt
```

## Basic Usage
```python
from research_analyzer import DomainConfiguration, ResearchAnalyzer, ConfigurationManager, ResearchDomain

# Create a configuration for psychology research
gm = ConfigurationManager()
config = gm.create_template(ResearchDomain.PSYCHOLOGY)
config.domain_name = "Stress and Coping Research"
config.research_objectives = [
    "Identify stress response patterns",
    "Analyze coping mechanisms",
    "Understand individual differences"
]

analyzer = ResearchAnalyzer(config)
documents = [
    "Participants reported high levels of stress during the exam period...",
    "Coping mechanisms varied significantly across individuals...",
]
results = analyzer.analyze_documents(documents)
print(f"Found {results['topics']['topic_count']} topics")
```

## License
MIT 