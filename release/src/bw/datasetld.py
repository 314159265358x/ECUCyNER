r"""
Copyright (C) haoyus@our.ecu.edu.au. All rights reserved.
This file convert the dataset to records and put in tensor, prepare for training and testing.
References:
https://pytorch.org/tutorials/beginner/nlp/advanced_tutorial.html
"""


import json
import torch

from .wordindex import WordIndex
from .tagindex import TagIndex
from .entityc import EntityC

class DatasetLoader(): ...
class DatasetLoader():
    data:list[EntityC]=[]
    word_idx:WordIndex=None
    tag_idx:TagIndex=None
    proc_cache:(list[torch.Tensor],list[torch.Tensor])=None

    def __init__(this) -> None:
        this.data:list[EntityC]=[]
        this.word_idx:WordIndex=None
        this.tag_idx:TagIndex=None

    def loadFile(this,path:str)->DatasetLoader:
        with open(path,'r') as fp:
            while True:
                ln:str=fp.readline()
                if not ln:
                    break
                if not ln.strip():
                    continue
                e:EntityC=EntityC().fromDict(json.loads(ln))
                this.data.append(e)
        this.proc_cache=None
        return this
    
    def setTagIndex(this,idx:TagIndex)->DatasetLoader:
        this.tag_idx=idx
        return this

    def setWordIndex(this,idx:WordIndex)->DatasetLoader:
        this.word_idx=idx
        return this
    """ ================ Dataset ================ """
    def prepare(this)->list[dict[str,torch.Tensor]]:
        if None!=this.proc_cache:
            return this.proc_cache
        proced:list[dict[str,torch.Tensor]]=[]
        for i in this.data:
            proced.append({
                'w':torch.tensor(
                    data=[this.word_idx.get(j) for j in i.words],
                    dtype=torch.long
                ),
                'l':torch.tensor(
                    [this.tag_idx.Lf2id(j) for j in i.labels],
                    dtype=torch.long
                )
            })
        this.proc_cache=proced
        return this.proc_cache