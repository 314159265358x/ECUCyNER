r"""
Retrieved from:
https://github.com/aiforsec/CyNER/blob/main/cyner/entity_extraction.py
"""
from abc import ABC, abstractmethod
from .entity import Entity

class EntityExtraction(ABC):
    @abstractmethod
    def __init__(self, config: dict):
        """
        initialize entity extraction model
        """
        pass

    @abstractmethod
    def get_entities(self, text:str)->list[Entity]:
        """

        :param text: input text
        :return: List of Entity objects
        """
        pass
