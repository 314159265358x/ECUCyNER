r"""
Retrieved from:
https://github.com/aiforsec/CyNER/blob/main/cyner/cyner.py
"""

from .entity_extraction_factory import get_entity_extraction_model
from .entity_extraction import EntityExtraction
from .entity import Entity

class CyNER(): 
    def __init__(self,
                 use_heuristic:bool=True, 
                 flair_model:str='ner', 
                 spacy_model:str='en_core_web_trf', 
                 priority:str='HFS'):
        self.heuristic_ner = None
        if use_heuristic:
            self.heuristic_ner = get_entity_extraction_model('heuristics', {})
        self.flair_ner = None
        if flair_model:
            self.flair_ner = get_entity_extraction_model('flair', {'model': flair_model})
        self.spacy_ner = None
        if spacy_model:
            self.spacy_ner = get_entity_extraction_model('spacy', {'model': spacy_model})
        self.priority = priority
        
    def get_model_corresponding_to_priority(self, letter:str)->EntityExtraction:
        if letter.upper() == 'H':
            return self.heuristic_ner
        elif letter.upper() == 'F':
            return self.flair_ner
        elif letter.upper() == 'S':
            return self.spacy_ner
        else:
            raise ValueError('Unknown letter in priority, must be in [HFS]')
            
    def construct_priority_model_list(self)->list[EntityExtraction]:
        models:list[EntityExtraction] = []
        
        for letter in self.priority:
            m:EntityExtraction = self.get_model_corresponding_to_priority(letter)
            if m is not None:
                models.append(m)
        return models
    
    def check_overlap(self, entities:list[Entity], candidate:Entity)->bool:
        for e in entities:
            if candidate.start >= e.start and candidate.start < e.end:
                return True
            if candidate.end -1 >= e.start and candidate.end <= e.end:
                return True
            if candidate.start <= e.start and candidate.end >= e.end:
                return True
        return False
    
    def merge_entities(self,cur_entities:list[Entity], candidate_entities:list[Entity])->list[Entity]:
        for candidate in candidate_entities:
            if not self.check_overlap(cur_entities, candidate):
                cur_entities.append(candidate)
        return cur_entities
    
    def get_entities(self, text:str)->list[Entity]:
        merged_entities:list[Entity] = []
        models:list[EntityExtraction] = self.construct_priority_model_list()
        
        for model in models:
            entities:list[Entity] = model.get_entities(text)
            merged_entities:list[Entity] = self.merge_entities(merged_entities, entities)
        return merged_entities
