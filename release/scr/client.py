r"""
Copyright (C) haoyus@our.ecu.edu.au. CC BY-SA 4.0.
this script is used to check the runtime environment of both pytorch and tensorflow
e.g. cuda availability, dependency integrity
"""

# ================ begin header ================
class Entity():
    start:int
    end:int
    entity_type:str
    text:str
    confidence:float # deprecated, will not have a value

    def deserialize(this,data:dict,text:str)->None:
        this.start=data['o']
        this.end=data['e']
        this.entity_type=data['t']
        this.text=text[this.start:this.end]

    def __dict__(this)->dict:
        return {
            'o':this.start,
            'e':this.end,
            't':this.entity_type,
            'w':this.text
        }
    
    def __str__(this)->dict:
        return json.dumps({
            'o':this.start,
            'e':this.end,
            't':this.entity_type,
            'w':this.text
        })

def callCynerSystem(text:str)->list[Entity]: ...
# ================ end header ================

import requests
import json
# this is the basic interface for group members which will use.
def callCynerSystem(text:str)->list[Entity]:
    response:requests.Response=requests.post(url='http://localhost:38080/',data=text)
    result_json:list[dict]=json.loads(response.text)
    result_obj:list[Entity]=[]
    for i in result_json:
        e:Entity=Entity()
        e.deserialize(i,text)
        result_obj.append(e)
    return result_obj




