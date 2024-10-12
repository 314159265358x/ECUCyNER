r"""
Copyright (C) haoyus@our.ecu.edu.au. All rights reserved.
This is the annotated label class of raw sentences.
EntityP: text:str, labels:list[EntityT]
"""

class EntityT(): ...
class EntityP(): ...

class EntityT():

    def __init__(this,p:EntityP) -> None:
        this.parent=p
    # in UTF-8 Char view (NOT Binary Byte view)
    offset:int=0
    length:int=0
    confidence:float=-1.0
    tag:str=None

    def __str__(this)->str:
        return 'Mention: {}, Class: {}, Start: {}, End: {}, Confidence: {:.2f}'.\
            format(this.getText(),this.tag,this.offset,this.offset+this.length,this.confidence)

    def getText(this)->str:
        return this.parent.text[this.offset:(this.offset+this.length)]

    def loadDeserialize(this,o:dict)->EntityT:
        this.offset=o['o']
        this.length=o['l']
        this.confidence=o['c'] if 'c' in o else -1.0
        this.tag=o['t'].lower()
        if (this.offset+this.length)>len(this.parent.text):
            raise RuntimeError('7')
        return this

    def saveSeralize(this,has_us:bool=False)->dict:
        if has_us:
            return {
                'o':this.offset,
                'l':this.length,
                'e':this.offset+this.length,
                't':this.tag
            }
        r:dict= {
            'o':this.offset,
            'l':this.length,
            't':this.tag
        }
        if -1.0 != this.confidence:
            r['c']=this.confidence
        return r
    
    def saveCynerEntity(this)->dict:
        return {
            "start":this.offset,
            "end":this.offset+this.length,
            "text":this.getText(),
            "entity_type":this.tag,
            "confidence":this.confidence
        }