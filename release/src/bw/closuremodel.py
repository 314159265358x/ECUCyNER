r"""
Copyright (C) haoyus@our.ecu.edu.au. All rights reserved.
this class is used to help the core module for:
keep necessary variable
save and load the content
References:
https://pytorch.org/tutorials/beginner/saving_loading_models.html
"""

import os
import torch
import json

from .tagindex import TagIndex
from .wordindex import WordIndex
from .bilstm_crf import BiLSTM_CRF

class ClosureModel(): ...
class ClosureModel():
    path:str=None
    tag_index:TagIndex=None
    word_index:WordIndex=None
    native:BiLSTM_CRF=None
    hyper_param:dict=None

    def __init__(self) -> None:
        pass
    
    def create(this,
               path:str=None,
               hyper_param:dict=None,
               tag_index:TagIndex=None,
               word_index:WordIndex=None):
        if None==hyper_param:
            hyper_param={
                'embedding_dim':5,
                'hidden_dim':4
            }
        this.hyper_param=hyper_param
        this.path=path
        this.word_index=word_index
        this.tag_index=tag_index

        this.native = BiLSTM_CRF(
            this.word_index.size(),
            this.tag_index,
            embedding_dim=this.hyper_param['embedding_dim'], 
            hidden_dim=this.hyper_param['hidden_dim'])
        pass

    def load(this,path:str):
        this.path=path
        
        config:dict={}
        with open(os.path.join(this.path,'closure.json'),'r') as fp:
            config=json.load(fp)
        this.hyper_param=config['hyper_param']

        this.word_index=WordIndex()
        with open(os.path.join(this.path,"word_index.json"),'r') as fp:
            this.word_index.loadDeserialize(json.load(fp))
        this.word_index.setWrite(False)
        this.tag_index=TagIndex()
        with open(os.path.join(this.path,"tag_index.json"),'r') as fp:
            this.tag_index.loadDeserialize(json.load(fp))

        this.native = BiLSTM_CRF(
            this.word_index.size(),
            this.tag_index,
            embedding_dim=this.hyper_param['embedding_dim'], 
            hidden_dim=this.hyper_param['hidden_dim'])
        this.native.load_state_dict(torch.load(os.path.join(this.path,"model.pth")))

        pass

    def save(this):
        if not os.path.isdir(this.path):
            os.makedirs(this.path)

        with open(os.path.join(this.path,'closure.json'),'w+') as fp:
            json.dump({
                'hyper_param':this.hyper_param
            },fp)

        with open(os.path.join(this.path,"word_index.json"),'w') as fp:
            json.dump(obj=this.word_index.saveSerialize(),fp=fp)
        with open(os.path.join(this.path,"tag_index.json"),'w') as fp:
            json.dump(obj=this.tag_index.saveSerialize(),fp=fp)

        torch.save(this.native.state_dict(), os.path.join(this.path,"model.pth"))
    
