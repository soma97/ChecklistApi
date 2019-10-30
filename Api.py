import flask
from flask import request,Response
import datetime
import json
from Checklist import Checklist
from Item import Item
from DAO import DB_access


def get_dec(func):
    def wrapper(*args,**kwargs):
        args=[1,2,3,4,5] # demonstration for positional args
        if "ChecklistID" in request.args:
            kwargs['checklist_id'] = request.args.get("ChecklistID")
            print(args)
        else:
            kwargs['checklist_id'] = None
        return func(*args,**kwargs)
    return wrapper



app = flask.Flask(__name__)
app.config["DEBUG"] = True

accessDB=DB_access()

@app.route('/', methods=['GET']) #get all checklists for user named in name param in URL or all items for checklist ChecklistID:int as param in URL (?name={name} or ?name={name}&ChecklistID={checklist id})
@get_dec
def home(a,b,*args,checklist_id):

    print(a+b,checklist_id) # a and b are demonstration how positional args work

    if 'name' not in request.args:
        return "Error: No username field provided. Please specify an username.",404

    if checklist_id != None:
        items=accessDB.get_items_for_checklist(checklist_id)
        res=[]
        for item in items:
            res.append(Item(item[0],item[1],item[2],item[3],item[4],item[5]))
        return json.dumps(res,default=lambda o: o.isoformat() if isinstance (o,datetime.datetime) else o.__dict__)
    
    chklists=[]

    try:
        rows=accessDB.get_checklist_for_name(request.args.get('name'))
    except:
        return "Checklists don't exist",404

    for row in rows:
        chklists.append(Checklist(row[0],row[1],row[2]))

    for one_checklist in chklists:
        try:
            items=accessDB.get_items_for_checklist(one_checklist.id)
            for item in items:
                one_checklist.items.append(Item(item[0],item[1],item[2],item[3],item[4],item[5]))
        except:
            pass

    return json.dumps(chklists,default=lambda o: o.isoformat() if isinstance (o,datetime.datetime) else o.__dict__)
    #return json.dumps([elem for elem in chklists if elem.username==request.args.get('name')],default=lambda o: o.isoformat() if isinstance (o,datetime.datetime) else o.__dict__)
  
    
#freq is frequency (daily,weekly or monthly) of item
@app.route('/', methods=['POST']) #insert or update item in checklist, mandatory args are "ChecklistID" : int , ("Item" : string and "Freq" : string) or ("ItemID" : int and "isDone" : bool) with name?={name} param in URL
def post():
    if "name" in request.args:

        req_checklist=request.get_json().get("ChecklistID")
        if "isDone" in str(request.get_data()):
            item_id=request.get_json().get("ItemID")
            done=request.get_json().get("isDone")
            accessDB.set_done(item_id,done)
            return "OK",200

        accessDB.insert_item(req_checklist,Item(None,request.get_json().get("Item"),datetime.datetime.now(),request.get_json().get("Freq"),False,None))
        return "OK",200
        
    else:
        return "Error: No username field provided. Please specify an username.",404

@app.route('/',methods=['PUT']) #insert checklist or user, mandatory args are "Checklist" : string with name?={name} param in URL or "User" : string without name param in URL 
def put():
    if 'name' in request.args:
        try:
            accessDB.insert_checklist(Checklist(None,request.get_json().get("Checklist"),request.args.get("name")))
            return "OK",200
        except:
            print('Incorrect username or request body')
            return "Bad request",400
    else:
        username=request.get_json().get("User")
        try:
            accessDB.insert_user(username)
            return "OK",200
        except:
            return "Bad request",400


@app.route('/',methods=['DELETE']) #delete checklist or item in checklist, mandatory args are "ChecklistID" : int or "ItemID" : int with name?={name} param in URL
def delete():
    if "name" in request.args:
        try:
            if "ChecklistID" in str(request.get_data()):
                accessDB.delete_checklist(request.get_json().get("ChecklistID"),request.args.get("name"))
            else:
                print("ASA")
                accessDB.delete_item(request.get_json().get("ItemID"))
            return "OK",200
        except:
            return "Checklist does not exist",404
    else:
        return "Error: No username field provided. Please specify an username.",404


app.run(port=7500)