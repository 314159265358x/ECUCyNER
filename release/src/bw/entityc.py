r"""
Copyright (C) haoyus@our.ecu.edu.au. All rights reserved.
This is the data structure of converted in split sentence, prepare for tagging
{
'words':['This','is','a','book'],
'labels':['O','O','O','B'],
}
"""

class EntityC(): ...
class EntityC():
    labels:list[str]=[] # bioes-mention 
    words:list[str]=[] # raw word

    def toDict(this)->dict:
        return {
            'l':this.labels,
            'w':this.words
        }
    
    def fromDict(this,dat:dict)->EntityC:
        this.labels=dat['l']
        this.words=dat['w']
        return this