r"""
Retrieved from:
https://github.com/aiforsec/CyNER/blob/main/cyner/tner/get_dataset.py#L221

this class download the BC5CDR dataset and process to the specific format below:
o1.data.txt # first split data
...
o5.data.txt # last split data
meta.word.txt # known words
meta.tag.txt # known tags
"""

import asyncio
import json
import os
import random
import shutil
from abc import ABC, abstractmethod
import traceback
from types import coroutine

import zipfile
import re
import requests

from .entityt import EntityT
from .entityp import EntityP
from .entitym import entityP2C

class DatasetDownloader(ABC):
    """
    0 None
    1 pending
    2 success
    3 error
    """
    status:int=0 # return
    out_file:str=None # param
    tmp_dir:str=None # param
    p:coroutine=None # private

    @staticmethod
    def runAll(that:list):
        all:list[coroutine]=[]
        for i in that:
            all.append(i.start())
        return asyncio.run(DatasetDownloader.runAllS1(all))

    @staticmethod
    async def runAllS1(that:list[coroutine]):
        return await asyncio.gather(*that)

    def __init__(this) -> None:
        this.status=1
        this.tmp_dir="/tmp/t-"+str(os.getpid())+'-'+(''.join(random.choice("def0987612345cba") for i in range(16)))

    def start(this)->coroutine:
        if 1!=this.status:
            raise RuntimeError('b')
        if None != this.p:
            return this.p
        this.p=this.run()
        return this.p

    async def run(this):
        try:
            await this.process()
            this.status=2
        except:
            this.status=3
            traceback.print_exc()

    @abstractmethod
    async def process()->None:
        pass

class DatasetDownloaderBC5CDR(DatasetDownloader):

    async def processSingle(this,file_in:str,file_out:str,file_meta:str):
        #parsed_entity:list[EntityP]=[]
        raw:list[str]=[]
        meta_word:list[str]=[]
        meta_tag:list[str]=[]
        with open(file_in,'r') as fp:
            raw = list(filter(lambda _x: len(_x) > 0, fp.read().split('\n\n')))

        with open(file_out,'a') as fp:
            for i in raw:
                lines:list[str]=i.split('\n')
                pp:EntityP=EntityP()
                text_t:str=None
                text_a:str=None
                pi:int=-1
                pt:list[EntityT]=[]
                for l in lines:
                    if None != re.match('^[0-9]+\t[0-9]+\t[0-9]+\t',l):
                        zv:list[str]=l.split('\t')
                        t:EntityT=EntityT(pp)
                        t.offset=int(zv[1])
                        t.length=int(zv[2])-t.offset
                        t.tag=zv[4].lower()
                        pt.append(t)
                        if not t.tag in meta_tag:
                            meta_tag.append(t.tag)
                        pii:int=int(zv[0])
                        if -1 == pi:
                            pi=pii
                        elif pii!=pi:
                            raise RuntimeError('c')
                    elif None != re.match('^[0-9]+\|[at]{1}\|',l):
                        zv:list[str]=l.split(r'|')
                        tl_r:str=zv[2]
                        tl_t:str=zv[1]
                        pii:int=int(zv[0])
                        if 't' == tl_t:
                            text_t=tl_r
                        elif 'a' == tl_t:
                            text_a=tl_r
                        else:
                            raise RuntimeError('d')
                        if -1 == pi:
                            pi=pii
                        elif pii!=pi:
                            raise RuntimeError('c')
                l=t=zv=pii=tl_r=tl_t=None
                if None==text_t or None==text_a:
                    print('incomplete data: \n'+json.dumps(i))
                    continue
                pp.id=pi
                pp.labels=pt
                last_tag:EntityT=None
                for ti1 in pp.labels:
                    if None==last_tag or last_tag.offset<ti1.offset:
                        last_tag=ti1
                text_indent:str=''
                if None!=last_tag and last_tag.offset>len(text_t):
                    zvc:list[str]=None
                    for l in lines:
                        if None != re.match('^[0-9]+\t[0-9]+\t[0-9]+\t',l):
                            zv:list[str]=l.split('\t')
                            if last_tag.offset==int(zv[1]):
                                zvc=zv
                                break
                    tt_raw_str:str=zvc[3]
                    ind_nj:int=0
                    while True:
                        if ind_nj> 16:
                            raise RuntimeError('f')
                        mm:int=last_tag.offset-len(text_t)-ind_nj
                        if tt_raw_str==text_a[mm:(mm+last_tag.length)]:
                            break
                        ind_nj=ind_nj+1
                    match(ind_nj):
                        case 0:
                            text_indent=''
                        case 1:
                            text_indent='\n'
                        case _:
                            text_indent=(' '*(ind_nj-1))+'\n'
                                    
                pp.text=text_t+text_indent+text_a
                #parsed_entity.append(pp)
                for i in re.findall("[a-zA-Z0-9]+",text_t):
                    if not i in meta_word:
                        meta_word.append(i)
                for i in re.findall("[a-zA-Z0-9]+",text_a):
                    if not i in meta_word:
                        meta_word.append(i)
        
                serialized_entity:str=json.dumps(
                    entityP2C(pp).toDict()
                    ,separators=(',',':'))
                fp.write(serialized_entity)
                fp.write('\n')

        with open(file_meta,'a') as fp:
            json.dump({
                'w':meta_word,
                't':meta_tag
            },fp)

    async def process(this):
        # https://github.com/aiforsec/CyNER/blob/main/cyner/tner/get_dataset.py#L218

        this_tmp_dir:str=this.tmp_dir
        if os.path.exists(this_tmp_dir):
            shutil.rmtree(this_tmp_dir)
        os.makedirs(this_tmp_dir)
        saved_file:str=os.path.join(this_tmp_dir,"CDR_Data.zip")
        with open(saved_file, "wb") as f:
            r = requests.get('https://github.com/JHnlp/BioCreative-V-CDR-Corpus/raw/master/CDR_Data.zip')
            f.write(r.content)
        # finish download at ${tmp_dir}/CDR_Data.zip
        with zipfile.ZipFile(saved_file, 'r') as zip_ref:
            zip_ref.extractall(this_tmp_dir)

        all_data_files:list[dict]=[
            {"i":"CDR_Data/tmChem.TestSet/TestSet.tmChem.PubTator.txt","o":"o1.data.txt","m":"m1.txt"},
            {"i":"CDR_Data/CDR.Corpus.v010516/CDR_TestSet.PubTator.txt","o":"o2.data.txt","m":"m2.txt"},
            {"i":"CDR_Data/CDR.Corpus.v010516/CDR_TrainingSet.PubTator.txt","o":"o3.data.txt","m":"m3.txt"},
            {"i":"CDR_Data/CDR.Corpus.v010516/CDR_DevelopmentSet.PubTator.txt","o":"o4.data.txt","m":"m4.txt"},
            {"i":"CDR_Data/DNorm.TestSet/TestSet.DNorm.PubTator.txt","o":"o5.data.txt","m":"m5.txt"}
            ]

        tasks:list[coroutine]=[]
        for i in all_data_files:
            fi:str=os.path.join(this_tmp_dir,i['i'])
            fo:str=os.path.join(this.out_file,i['o'])
            fm:str=os.path.join(this.out_file,i['m'])
            tp:coroutine=this.processSingle(fi,fo,fm)
            tasks.append(tp)
        if not os.path.isdir(this.out_file):
            os.makedirs(this.out_file)
        await asyncio.gather(*tasks)
        shutil.rmtree(this.tmp_dir)

        meta_word:list[str]=[]
        meta_tag:list[str]=[]
        for i in all_data_files:
            fm:str=os.path.join(this.out_file,i['m'])
            with open(fm,'r') as fp:
                o=json.load(fp)
                meta_word=list(set(meta_word) | set(o['w']))
                meta_tag=list(set(meta_tag) | set(o['t']))
            os.remove(fm)
        meta_word_out=[i+'\n' for i in meta_word]
        meta_tag_out=[i+'\n' for i in meta_tag]
        with open(os.path.join(this.out_file,'meta.word.txt'),'w') as fp:
            fp.writelines(meta_word_out)
        with open(os.path.join(this.out_file,'meta.tag.txt'),'w') as fp:
            fp.writelines(meta_tag_out)
