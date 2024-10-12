r"""
Retrieved from:
https://github.com/aiforsec/CyNER/blob/main/cyner/entity.py
"""
class Entity:
    start:int
    end:int
    text:str
    entity_type:str
    confidence:float

    def __init__(self, start:int, end:int, text:str, entity_type:str, confidence:float=1):
        """
        :param start: start position of the entity in the source text
        :param end: end position of the entity in the source text
        :param text: entity text
        :param entity_type: type of the entity
        :param confidence: probability or confidence (range [0, 1])
        """
        self.start = start
        self.end = end
        self.text = text
        self.entity_type = entity_type
        self.confidence = confidence

    def __str__(self):
        return 'Mention: {}, Class: {}, Start: {}, End: {}, Confidence: {:.2f}'.\
            format(self.text, self.entity_type, self.start, self.end, self.confidence)

    def toRemoteDict(this)->dict:
        return {
            'o':this.start,
            'l':(this.end-this.start),
            'e':this.end,
            't':this.entity_type
        }

    def toDict(this)->dict:
        return {
            'o':this.start,
            'l':(this.end-this.start),
            'e':this.end,
            't':this.entity_type,
            'c':this.confidence,
            'r':this.text
        }
