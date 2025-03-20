from flask import Flask, request, jsonify
from dbModel import SqliteModelV3
import json
import jsonpickle


app = Flask(__name__)
path = "/home/LordRajaBabu/mysite/abc.sqlite"
model = SqliteModelV3()
model.s.process.filePath = path

@app.route('/')
def home():
    helps = """

    /create POST {loc: [], value: any} <br>
    /read POST {loc: []} => {result: any} <br>
    /readTables GET => {"tables": str[]} <br>
    /delete POST {loc: []} => {result: any} <br>
    /exists POST {loc: []} => {result: true|false} <br>

    """
    return helps

@app.route('/readKeys', methods=['POST'])
def readKeys():
    loc = request.get_json()["loc"]
    val = model.read(loc)
    if type(loc) == dict:
        return jsonify(list(val.keys()))
    elif type(loc) == list:
        return jsonify(list(val))
    return val

@app.route('/read', methods=['POST'])
def read():
    inps = request.get_json()
    loc = inps["loc"]
    mode = "str"
    if "mode" in inps and inps["mode"] == "py":
        mode = "py"
    
    val = model.read(loc)
    if mode == "py":
        return jsonpickle.encode(val)
    return json.dumps(val, default=str)
@app.route('/create', methods=['POST'])
def create():
    inps = request.get_json()
    loc = inps["loc"]
    value = inps["value"]
    model.add(loc, value)
    return "created successfully"

@app.route('/delete', methods=['POST'])
def delete():
    loc = request.get_json()["loc"]
    model.delete(loc)
    return "deleted successfully"

@app.route('/exists', methods=['POST'])
def exists():
    loc = request.get_json()["loc"]
    return {"result":  model.exists(loc)}


@app.route('/readKeysValue', methods=['POST'])
def readKeysValue():
    inps = request.get_json()
    loc = inps["loc"]
    val = model.read(loc)
    keys = inps["keys"]
    res ={k: val[k] for k in keys}
    mode = "str"
    if "mode" in inps and inps["mode"] == "py":
        mode = "py"
    if mode == "py":
        return jsonpickle.encode(res)
    return json.dumps(res, default=str)

