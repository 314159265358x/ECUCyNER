r"""
Copyright (C) haoyus@our.ecu.edu.au. All rights reserved.
this class is the main class control the whole project loading and running process.
main -> loading config -> loading LSTM -> loading CyNER -> start loop service
loop -> listen port (http post) from reverse proxy (NGINX) -> detect in LSTM -> detect in CyNER -> return tagging data 
"""
import bw
import cyner
import flask
import json
import traceback

class TaskDist():
    bw_model:bw.ClosureModel=None
    cyner_model:cyner.CyNER=None
    handler:flask.Flask=None
    opt:dict=None

    def load(this, opt:dict)->None:
        this.opt=opt
        this.bw_model=bw.simpleWrapperLoadModel(**this.opt['bw'])
        this.cyner_model=cyner.CyNER(**this.opt['cyner'])
        this.handler=app=flask.Flask(this.opt['listen']['name'])
        app.config['MAX_CONTENT_LENGTH']=this.opt['listen']['max_len']
        app.add_url_rule(rule='/',endpoint='rmcb',view_func=this.remoteCallback,methods=['POST'],defaults={'path': ''})
        app.add_url_rule(rule='/<path:path>',endpoint='rmcb',view_func=this.remoteCallback,methods=['POST'])

    def run(this):
        this.handler.run(port=this.opt['listen']['port'])
        
    # ================================================================

    def remoteCallback(this,path)->flask.Response:
        try:
            req:flask.Request=flask.request
            text=req.get_data(as_text=True,parse_form_data=False)
            print("request: "+text)
            out_raw:dict=this.predict(text)
            out_str:str=json.dumps(out_raw)
            print("response: "+out_str)
            return flask.Response(response=out_str,mimetype='application/json')
        except:
            print(traceback.format_exc())

    def predict(this,text:str)->list[dict]:
        bw_ret:bw.EntityP=bw.simpleWrapperPredict(this.bw_model,text)
        bw_rd:list[dict]=[i.saveSeralize(has_us=True) for i in bw_ret.labels]
        cyner_ret:list[cyner.Entity]=this.cyner_model.get_entities(text=text)
        cyner_rd:list[dict]=[i.toRemoteDict() for i in cyner_ret]
        final_out:list[dict]=[]
        for i in bw_rd:
            if not this.check_overlap(final_out, i):
                final_out.append(i)
        for i in cyner_rd:
            if not this.check_overlap(final_out, i):
                final_out.append(i)
        return final_out
    
    @staticmethod
    def check_overlap(entities:list[dict],candidate:dict)->bool:
        for e in entities:
            if candidate['o'] >= e['o'] and candidate['o'] < e['e']:
                return True
            if candidate['e'] -1 >= e['o'] and candidate['e'] <= e['e']:
                return True
            if candidate['o'] <= e['o'] and candidate['e'] >= e['e']:
                return True
        return False

def main()->None:
    task_dist:TaskDist=TaskDist()
    opt:dict=None
    with open("res/settings.json",'r') as fp:
        opt=json.load(fp)
    task_dist.load(opt)
    task_dist.run()

if __name__ == '__main__':
    main()
