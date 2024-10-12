r"""
Copyright (C) haoyus@our.ecu.edu.au. All rights reserved.
This is a convertor between raw format and split format.
"""

import json
import re

from .entityp import EntityP
from .entityt import EntityT
from .entityc import EntityC

def entityP2C(
        entity_entry:EntityP,
        )->EntityC:
    text_raw:str=entity_entry.getText()
    out_word:list[str]=re.findall("[a-zA-Z0-9]+",text_raw)

    out_len=len(out_word)
    out_tag:list[str]=['']*out_len
    cur_stripos:int=0
    cur_apos:int=0

    while True:
        if cur_apos>=out_len:
            break
        cur_word:str=out_word[cur_apos]
        cur_stripos=text_raw.find(cur_word,cur_stripos)

        possible_tag:list[str]=[]
        for each_tag in entity_entry.labels:
            if each_tag.offset<(cur_stripos+len(cur_word)) and (each_tag.offset+each_tag.length)>cur_stripos:
                if not each_tag.tag in possible_tag:
                    possible_tag.append(each_tag.tag)
        if len(possible_tag)>1:
            raise RuntimeError('invalid tag: \n'+
                               json.dumps(entity_entry.saveSerialize())+'\n'+
                               str(cur_stripos)+'\t'+cur_word+'\n'
                               
                               )
        if 0==len(possible_tag):
            out_tag[cur_apos]='o'
        elif 0==cur_apos:
            out_tag[cur_apos]='b-'+possible_tag[0].lower()
        else:
            last_tag:str=out_tag[cur_apos-1]
            last_tagname:str=''
            if len(last_tag)>2:
                last_tagname=last_tag[2:]
            if last_tagname==possible_tag[0]:
                out_tag[cur_apos]='i-'+last_tagname
            else:
                out_tag[cur_apos]='b-'+possible_tag[0].lower()
        cur_stripos=cur_stripos+len(cur_word)
        cur_apos=cur_apos+1
    return EntityC().fromDict({'l':out_tag,'w':out_word})

def entityC2P(
        text_raw:str,
        out_component:EntityC,
        )->EntityP:
    token_len:int=len(out_component.labels)
    assert token_len==len(out_component.words)
    result:EntityP=EntityP().loadEmpty(t=text_raw)
    cur_out:int=0 # loop cur offset in out_token
    cur_raw:int=0 # loop cur offset in text_raw, always point to last indent char before current object
    last_tag:EntityT=None # last parsed tag obj
    last_token:int='o' # last parsed tag token
    #last_token_bio:str='o' # last parsed tag bio
    last_token_qn:str='' # last parsed tag qn
    while True:
        if token_len == cur_out:
            break
        cur_token:int=out_component.labels[cur_out]
        cur_token_bio:str=cur_token[0]
        cur_token_qn:str=cur_token[2:]
        next_action:int=0
        """
        0: nothing
        1: create new
        2: commit exist
        3: expand exist
        4: commit and create
        """
        if 'o'==cur_token: # ?, o
            if 'o'==last_token:
                next_action=0 # o, o
            else:
                next_action=2 # b/i-, o
        elif 'i'==cur_token_bio: # b-, i-
            if last_token_qn == cur_token_qn: # b/i-a, i-a
                next_action=3 # expand marked
            elif 'o'==last_token:
                next_action=1 # o, i- should not occur in normal. small mistake, treat as o, b-
            else:
                next_action=4 # b/i-a, i-b should not occur in normal. for safety, fall back to b/i-a, b-b
        elif 'b'==cur_token_bio: # ?, b-
            if 'o'==last_token:
                next_action=1 # o, b-
            else:
                next_action=2 # b/i-, b-
        match(next_action):
            case 0:
                pass
            case 1:
                if None != last_tag:
                    raise LookupError('a')
                last_tag=EntityT(result)
                last_tag.offset=text_raw.find(out_component.words[cur_out],cur_raw)
                last_tag.tag=cur_token_qn
                result.labels.append(last_tag)
            case 2:
                if None == last_tag:
                    raise LookupError('b')
                last_tag.length=cur_raw-last_tag.offset
                last_tag=None
            case 3:
                if None == last_tag:
                    raise LookupError('b')
                last_tag.length=cur_raw-last_tag.offset
                last_tag=None # always force reset
                last_tag=EntityT(result)
                last_tag.offset=text_raw.find(out_component.words[cur_out],cur_raw)
                last_tag.tag=cur_token_qn
                result.labels.append(last_tag)
            case 4:
                pass # current version of marking method have nothing to do 
            case _:
                pass
        #last_token_bio=cur_token_bio
        last_token_qn=cur_token_qn
        last_token=cur_token
        cur_raw=text_raw.find(out_component.words[cur_out],cur_raw)+len(out_component.words[cur_out])
        cur_out=cur_out+1
    if None != last_tag:
        last_tag.length=cur_raw-last_tag.offset
        last_tag=None
    return result

__all__ = (
    "entityP2C",
    "entityC2P"
    )
