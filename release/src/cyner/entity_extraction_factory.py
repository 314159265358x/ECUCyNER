r"""
Retrieved from:
https://github.com/aiforsec/CyNER/blob/main/cyner/entity_extraction_factory.py
"""
from .entity_extraction import EntityExtraction
from .flair_ner import Flair
from .spacy_ner import Spacy
from .heuristics_ner import HeuristicsNER


def get_entity_extraction_model(name: str, config: dict) -> EntityExtraction:
    name = name.lower()
    if name == 'flair':
        return Flair(config)
    elif name == 'spacy':
        return Spacy(config)
    elif name == 'heuristics':
        return HeuristicsNER(config)
    else:
        raise ValueError('Unknown entity extraction model')

__all__=('get_entity_extraction_model')
