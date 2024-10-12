r"""
Copyright (C) haoyus@our.ecu.edu.au. All rights reserved.

this is the main process of model operating which contains:
create empty -> train -> save ; load ; predict

References:
https://pytorch.org/tutorials/_downloads/advanced_tutorial.py
https://pytorch.org/tutorials/beginner/nlp/advanced_tutorial.html

https://github.com/jidasheng/bi-lstm-crf
https://github.com/SenseKnowledge/pytorch-NER
https://github.com/glample/tagger
"""


import torch
from torch.utils.data import DataLoader as torch_DataLoader
import os
import random
from tqdm import tqdm

from torcheval.metrics import MulticlassAccuracy as torcheval_MulticlassAccuracy

from .closuremodel import ClosureModel
from .datasetdl import DatasetDownloader, DatasetDownloaderBC5CDR
from .wordindex import WordIndex
from .tagindex import TagIndex,TagIndexPreset
from .datasetld import DatasetLoader
from .entityp import EntityP
from .entityc import EntityC
from .entitym import entityC2P,entityP2C



def simpleWrapperLoadModel(
    hparg_epoch:int=20,
    hparg_test_count:int=50,
    hparam_embedding_dim:int=5,
    hparam_hidden_dim:int=4,
    opt_path_save:str='data',
    opt_path_tmp:str='',
    opt_torch_init:bool=True
)->ClosureModel:
    print("loading LSTM-CRF instance")
    print('pre-init')

    if ''==opt_path_tmp:
        opt_path_tmp="/tmp/t-"+str(os.getpid())+'-'+(''.join(random.choice("def0987612345cba") for i in range(16)))

    if opt_torch_init:
        torch.seed()
        #torch.set_default_tensor_type('torch.cuda.FloatTensor')
        torch.set_default_device('cuda')

    print('init')
    path_model:str=os.path.join(opt_path_save,'model')
    model:ClosureModel=None
    if not os.path.isdir(path_model):
        path_dataset:str=os.path.join(opt_path_save,'dataset')
        if not os.path.isdir(path_dataset):
            print('download dataset')
            dl:DatasetDownloaderBC5CDR=DatasetDownloaderBC5CDR()
            dl.out_file=path_dataset
            dl.tmp_dir=opt_path_tmp
            DatasetDownloader.runAll([dl])
        print('making word & tag index')
        datatset_files:list[str]=[]
        word_index:WordIndex=WordIndex()
        tag_index:TagIndex=None
        for file in os.listdir(os.fsencode(path_dataset)):
            filename = os.fsdecode(file)
            if filename.endswith(".data.txt"):
                datatset_files.append(filename)
            elif filename.endswith(".tag.txt"):
                with open(os.path.join(path_dataset,filename)) as fp:
                    tag_index_tmp:list[str]=fp.readlines()
                    tag_index_tmp_2:list[str]=[i[0:-1] for i in tag_index_tmp if '' != i]
                    tag_index=TagIndexPreset(tag_index_tmp_2)
                    del tag_index_tmp_2
                    del tag_index_tmp
            elif filename.endswith(".word.txt"):
                with open(os.path.join(path_dataset,filename)) as fp:
                    word_index_tmp:list[str]=fp.readlines()
                    word_index_tmp_2:list[str]=[i[0:-1] for i in word_index_tmp if '' != i]
                    word_index.new(len(word_index_tmp_2)+3)
                    word_index.fillAll(word_index_tmp_2)
                    del word_index_tmp
                    del word_index_tmp_2
        del file,filename
        print('create model')
        model=ClosureModel()
        model.create(
            hyper_param={
                'embedding_dim':hparam_embedding_dim,
                'hidden_dim':hparam_hidden_dim
            },
            tag_index=tag_index,
            word_index=word_index,
            path=path_model
        )
        print('load dataset')
        train_data_lz:DatasetLoader=DatasetLoader()
        train_data_lz.setTagIndex(model.tag_index)
        train_data_lz.setWordIndex(model.word_index)
        for i in datatset_files:
            train_data_lz.loadFile(os.path.join(path_dataset,i))
        del i
        test_data_lz:DatasetLoader=DatasetLoader()
        test_data_lz.setTagIndex(model.tag_index)
        test_data_lz.setWordIndex(model.word_index)
        for i in range(hparg_test_count):
            cur=random.choice(train_data_lz.data)
            train_data_lz.data.remove(cur)
            test_data_lz.data.append(cur)
        del i

        print('found train '+str(len(train_data_lz.data))+' and test '+str(len(test_data_lz.data)))
        optimizer:torch.optim.Adam=torch.optim.SGD(params=model.native.parameters(),lr=0.01,weight_decay=1e-4)

        val_loss_last:float=0.0
        print('training')
        for epoch in range(hparg_epoch):
            model.native.train()
            with tqdm(iterable=train_data_lz.prepare(),desc='Train '+format(epoch,'4d')) as t:
                for i, case in enumerate(t):
                    model.native.zero_grad()
                    loss = model.native.neg_log_likelihood(case['w'],case['l'])
                    loss.backward()
                    optimizer.step()
                    #t.update(1)
                    t.set_postfix(loss=float(loss))

            model.native.eval()
            with torch.no_grad():
                score = torcheval_MulticlassAccuracy(device=torch.device('cuda'))
                with tqdm(iterable=test_data_lz.prepare(),desc='Test  '+format(epoch,'4d')) as t:
                    for i, case in enumerate(t):
                        _,y_pred = model.native(case['w'])
                        #print('='*64+'\n'+str(type(y_pred))+', '+str(type(case['l'])))
                        score.update(torch.tensor(y_pred,device=torch.device('cuda')),torch.tensor(case['l'],device=torch.device('cuda')))
                val_loss=float(score.compute())
                if val_loss >= val_loss_last:
                    model.save()
                    val_loss_last=val_loss
                    print(str(val_loss)+' model saved')
                else:
                    print(val_loss)
    else:
        print('load model')
        model=ClosureModel()
        model.load(path_model)

    print("loaded LSTM-CRF instance")
    return model


def simpleWrapperPredict(
        model:ClosureModel,
        input:str,
        torch_cuda:bool=True
        )->EntityP:

    ep:EntityP=EntityP()
    ep.text=input
    ec:EntityC=entityP2C(ep)
    cc:list[int]=[model.word_index.get(i) for i in ec.words]

    sent_tensor = torch.tensor(cc,dtype=torch.long)

    if torch_cuda:
        sent_tensor=sent_tensor.cuda()

    model.native.eval()
    tags_raw=None
    with torch.no_grad():
        _, tags_raw = model.native(sent_tensor)

    ec.labels=[model.tag_index.Lid2f(i) for i in tags_raw]
    ep=entityC2P(text_raw=input,out_component=ec)
    return ep

__all__ = (
    "simpleWrapperLoadModel",
    "simpleWrapperPredict"
    )

