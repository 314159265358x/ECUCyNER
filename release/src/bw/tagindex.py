r"""
Copyright (C) haoyus@our.ecu.edu.au. All rights reserved.
this class keep the index between tag and id
"""

import json

class TagIndex: ...

class TagIndex():
    Vorigin:list[dict]=[]
    Vspec:dict[str:int]={} # o e s 

    Mid2full:dict[int,str]={} # id -> type-name
    Mfull2id:dict[str,int]={} # type-name -> id
    Mid2type:dict[int,str]={} # id -> type
    Mid2name:dict[int,str]={} # id -> name

    Vnextid:int=-1

    def Lid2t(this,id:int,o:str='o')->str:
        if id in this.Mid2type:
            return this.Mid2type[id]
        return o
    
    def Lid2n(this,id:int,o:str='')->str:
        if id in this.Mid2name:
            return this.Mid2name[id]
        return o
    
    def Lid2f(this,id:int,o:str='o')->str:
        if id in this.Mid2full:
            return this.Mid2full[id]
        return o
    
    def Lf2id(this,f:str,o:str='o')->int:
        f=f.lower()
        if f in this.Mfull2id:
            return this.Mfull2id[f]
        return this.Vspec[o]

    def Send(this)->int:
        return this.Vspec['e']
    
    def Sstart(this)->int:
        return this.Vspec['s']

    def saveSerialize(this)->dict:
        return {'t':this.Vorigin,'s':this.Vspec}
    
    def LlenType(this)->int:
        return len(this.Mid2full)
    
    def LmaxIdNext(this)->int:
        return this.Vnextid
    
    def loadDeserialize(this,r:dict)->TagIndex:
        o:list[dict]=r['t']
        this.Vorigin=o
        this.Vspec=r['s']

        this.Mid2full={}
        this.Mfull2id={}
        this.Mid2type={}
        this.Mid2name={}

        for i in o:
            if i['b'] in this.Mid2full or i['i'] in this.Mid2full:
                raise RuntimeError("kwtag register error 1, already conflict: "+str(i))
            if 'b-'+i['n'] in this.Mfull2id or 'i-'+i['n'] in this.Mfull2id:
                raise RuntimeError("kwtag register error 2, already conflict: "+str(i))

            this.Mid2full[i['b']]='b-'+i['n']
            this.Mid2full[i['i']]='i-'+i['n']
            this.Mfull2id['b-'+i['n']]=i['b']
            this.Mfull2id['i-'+i['n']]=i['i']

            this.Mid2type[i['b']]='b'
            this.Mid2type[i['i']]='i'
            this.Mid2name[i['b']]=i['n']
            this.Mid2name[i['i']]=i['n']
            for ii in i['a']:
                if 'b-'+ii in this.Mfull2id or 'i-'+ii in this.Mfull2id:
                    raise RuntimeError("kwtag register error 3, already conflict: "+str(i)+" -> "+ii)
                this.Mfull2id['b-'+ii]=i['b']
                this.Mfull2id['i-'+ii]=i['i']
        
        for i in this.Vspec:
            id:int=this.Vspec[i]
            this.Mfull2id[i]=id
            this.Mid2full[id]=i
            this.Mid2name[id]=''
            this.Mid2type[id]=i

        j:int=0
        for k in this.Mid2full:
            if k > j:
                j=k
        this.Vnextid=j+1
        return this


r"""
Shared label set across different 
no case sensitive
modified from https://github.com/aiforsec/CyNER/blob/main/cyner/tner/get_dataset.py#L33
"""
def TagIndexDefault()->TagIndex:
    with open('res/TagIndexDefault.json','r') as a:
        b=json.load(a)
        return TagIndex().loadDeserialize(b)

def TagIndexPreset(addtag:list[str]=None)->TagIndex:
    a:dict={
    "s": {
        "e": 2,
        "o": 0,
        "s": 1
    },
    "t": []
    }
    j:int=4
    for i in addtag:
        k:dict={
            "a": [],
            "b": j,
            "i": (j+1),
            "n": i
        }
        a['t'].append(k)
        j=j+2
    return TagIndex().loadDeserialize(a)

__all__ = ("TagIndex","TagIndexDefault","TagIndexPreset")
