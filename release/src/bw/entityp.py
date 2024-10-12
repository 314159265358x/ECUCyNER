r"""
Copyright (C) haoyus@our.ecu.edu.au. All rights reserved.
This is the root class of raw sentences.
"""

class EntityT(): ...
class EntityP(): ...

class EntityP():
    # savable content
    text:str=None
    labels:list[EntityT]=[]
    id:int=-1

    def getText(this)->str:
        return this.text

    def loadEmpty(this,t:str,i:int=-1)->EntityP:
        if this.text is not None:
            raise RuntimeError("1")
        this.text=t
        this.id=i
        this.labels=[]
        return this
    
    def loadDeserialize(this,o:dict)->EntityP:
        if this.text is not None:
            raise RuntimeError("2")
        this.text=o["t"]
        for i in o["l"]:
            this.labels.append(EntityT(this).loadDeserialize(i))
        this.id=o["i"] if 'i' in o else -1
        return this

    def saveSerialize(this)->dict:
        if this.text is None:
            raise RuntimeError("3")
        r:list=[]
        for i in this.labels:
            r.append(i.saveSeralize())
        r1:dict= {
            't':this.text,
            'l':r
        }
        if -1 != this.id:
            r1['i']=this.id
        return r1
