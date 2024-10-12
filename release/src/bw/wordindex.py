r"""
Copyright (C) haoyus@our.ecu.edu.au. All rights reserved.
this class keep the index between tag and id
"""

class WordIndex(): ...

class WordIndex():
    len_max:int=0
    len_cur:int=0

    w2i:dict[str,int]={}
    i2w:dict[int,str]={}

    w:bool=True


    def new(this,len_max:int)->WordIndex:
        this.len_cur=1
        this.len_max=len_max
        this.w2i={}
        this.i2w={}
        return this

    def loadDeserialize(this,o:dict)->WordIndex:
        this.len_cur=o['s']['len_cur']
        this.len_max=o['s']['len_max']
        this.w2i=o['d']
        this.i2w={}
        for i in this.w2i:
            j:int=this.w2i[i]
            this.i2w[j]=i
        return this

    def saveSerialize(this)->dict:
        return {
            'd':this.w2i,
            's':{
                'len_cur':this.len_cur,
                'len_max':this.len_max
            }
        }

    def setWrite(this,w:bool)->WordIndex:
        this.w=w
        return this
    
    def isWrite(this)->WordIndex:
        return this.w
    
    def fillAll(this,data:list[str])->WordIndex:
        if not this.w:
            raise RuntimeError('h')
        for i in data:
            if i in this.w2i:
                continue
            v2:int=this.len_cur
            if v2 >= this.len_max:
                this.len_max=v2
            this.len_cur=v2+1
            this.i2w[v2]=i
            this.w2i[i]=v2
        return this

    def get(this, k: str) -> int:
        if '' == k:
            return 0
        if k in this.w2i:
            return int(this.w2i[k])
        return 0

    def size(this) -> int:
        return this.len_cur
    