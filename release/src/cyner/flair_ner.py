r"""
Retrieved from:
https://github.com/aiforsec/CyNER/blob/main/cyner/flair_ner.py
this class has been updated for current version of flair model
"""
from flair.data import Sentence
from flair.models import SequenceTagger

from .entity_extraction import EntityExtraction
from .entity import Entity


class Flair(EntityExtraction):
    """
    Entity extraction using Flair NER model
    """
    def __init__(self, config):
        super().__init__(config)
        self.tagger = SequenceTagger.load(config['model'])

    def train(self):
        pass

    def get_entities(self, text):
        sentence = Sentence(text)
        self.tagger.predict(sentence)
        entities = []
        for x in sentence.get_labels(label_type='ner'):
            # 'labels' are formatted as [(TAG prob), ...]
            entities.append(Entity(x.data_point.start_position, x.data_point.end_position, x.data_point.text, x.value, x.data_point.score))
        return entities
