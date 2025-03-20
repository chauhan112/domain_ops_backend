
from sqlitedict import SqliteDict
import inspect
import dill as pickle
import gzip
class CompressDB:
    def content():
        class Temp:
            def compressToBinVal(content):
                return gzip.compress(content)
            def decompressFromBinVal(content):
                return gzip.decompress(content)
        return Temp
class SerializationDB:
    def readPickle(filePath):
        with open(filePath, 'rb') as f:
            binValCompressed = f.read()
        try:
            binVal = CompressDB.content().decompressFromBinVal(binValCompressed)
        except:
            binVal = binValCompressed
        return pickle.loads(binVal)
    def pickleOut(dataStructure, outFileName):
        data = pickle.dumps(dataStructure)
        dataCompressed = CompressDB.content().compressToBinVal(data)
        with open(outFileName, 'wb') as f:
            f.write(dataCompressed)
class DicOps:
    def get(dic, loc):
        val = dic
        for x in loc:
            val = val[x]
        return val
    def addEventKeyError(dic, loc, val):
        valT = dic
        lastKey = loc.pop()
        for x in loc:
            if type(valT) == dict and x not in valT:
                valT[x] = {}
            valT = valT[x]
        valT[lastKey] = val
def DictionaryModel():
    model = {}
    main_loc = []
    def changed():
        pass
    def goback():
        if len(s.process.main_loc) > 0:
            s.process.main_loc.pop()
    def goForward(key):
        s.process.main_loc.append(key)
    def add(loc, val):
        if not s.handlers.exists(loc):
            s.handlers.update(loc, val)
            s.handlers.changed()
    def read(loc=None):
        newLoc = s.handlers._get_loc(loc)
        return DicOps.get(s.process.model, newLoc)
    def update(loc, newValue):
        newLoc = s.handlers._get_loc(loc)
        DicOps.addEventKeyError(s.process.model, newLoc, newValue)
    def delete(loc):
        if len(loc) == 0:
            return
        elif type(loc) == str:
            loc = [loc]
        newLoc = loc.copy()
        lastKey = newLoc.pop()
        vals = s.handlers.read(newLoc)
        del vals[lastKey]
        s.handlers.changed()
    def exists(loc):
        try:
            s.handlers.read(loc)
            return True
        except:
            return False
    def readAll():
        return s.process.model
    def set_file(file):
        s.process.filePath = file
        s.process.model = SerializationDB.readPickle(file)
        def sync():
            SerializationDB.pickleOut(s.process.model, s.process.filePath)
        s.handlers.changed = sync
    def export(file):
        SerializationDB.pickleOut(s.process.model, file)
    def _get_loc(loc):
        newLoc = loc
        if newLoc is None:
            newLoc = s.process.main_loc
        elif type(newLoc) == str:
            newLoc = s.process.main_loc.copy() + [loc]
        return newLoc
    s = ObjMaker.variablesAndFunction(locals())
    s.handlers.s = s
    return s.handlers
class NameSpace:
    pass
class ObjectOps:
    def make_obj():
        return NameSpace()
    def setEvenIfItdoesNotExist(obj, loc, val):
        if len(loc) == 0:
            return
        newLoc = loc[:-1]
        innerObj = obj
        for key in newLoc:
            if not ObjectOps.exists(innerObj, [key]):
                ObjectOps.setter(innerObj, [key], ObjectOps.make_obj())
            innerObj = getattr(innerObj, key)
        key = loc[-1]
        setattr(innerObj, key, val)
    def exists(obj, loc):
        val = obj
        for key in loc:
            if not hasattr(val, key):
                return False
            val = getattr(val, key)
        return True
    def setter(obj, loc, val):
        if len(loc) == 0:
            return
        innerObj = ObjectOps.getter(obj, loc[:-1])
        key = loc[-1]
        setattr(innerObj, key, val)
    def getter(obj, loc):
        val = obj
        for key in loc:
            val = getattr(val, key)
        return val
class ObjMaker:
    def variablesAndFunction(dictVals, ignoring=[], obj=None, ignoreIfExistsInObj=False):
        if obj is None:
            obj = ObjectOps.make_obj()
        for key in dictVals:
            if key in ignoring:
                continue
            if hasattr(obj, key) and ignoreIfExistsInObj:
                continue
            val = dictVals[key]
            if inspect.isclass(val):
                pass
            elif inspect.isfunction(val):
                ObjectOps.setEvenIfItdoesNotExist(obj, ['handlers', key], val)
                ObjectOps.setEvenIfItdoesNotExist(obj, ['handlers', 'defs', key], val)
            else:
                ObjectOps.setEvenIfItdoesNotExist(obj, ['process', key], val)
        ObjectOps.setEvenIfItdoesNotExist(obj, ['local_states'], dictVals)
        return obj
def SqliteModelV3():
    dm = DictionaryModel()
    filePath = "test.sqlite"
    def readTableAsDic(table):
        with SqliteDict(s.process.filePath, tablename=table, autocommit=True) as db:
            return dict(db.iteritems())
    def read(loc):
        if len(loc)  == 0:
            tableNames = s.handlers.get_table_names()
            return tableNames
        if len(loc) == 1:
            return s.handlers.readTableAsDic(loc[0])
        else:
            with SqliteDict(s.process.filePath, tablename=loc[0], autocommit=True) as db:
                vals = db[loc[1]]
                s.process.dm.s.process.model = vals
                return dm.read(loc[2:])
    def delete(loc):
        if len(loc) == 1:
            with SqliteDict(s.process.filePath, autocommit=True) as db:
                db.conn.select_one(f'DROP TABLE "{loc[0]}"')
        elif len(loc) == 2:
            with SqliteDict(s.process.filePath, tablename=loc[0], autocommit=True) as db:
                del db[loc[1]]
        elif len(loc) > 2:
            tableName = loc[0]
            key = loc[1]
            with SqliteDict(s.process.filePath, tablename=tableName, autocommit=True) as db:
                vals = db[key]
                s.process.dm.s.process.model = vals
                s.process.dm.delete(loc[2:])
                db[key] = vals
    def add(loc, val):
        if len(loc) == 2:
            key = loc[1]
            with SqliteDict(s.process.filePath, tablename=loc[0], autocommit=True) as db:
                db[key] = val
        elif len(loc) > 2:
            tableName = loc[0]
            key = loc[1]
            with SqliteDict(s.process.filePath, tablename=tableName, autocommit=True) as db:
                vals = db.get(key)
                if vals is None:
                    vals = {}
                s.process.dm.s.process.model = vals
                s.process.dm.update(loc[2:], val)
                db[key] = vals
    def exists(loc):
        if len(loc) == 1:
            tables = s.handlers.get_table_names()
            return loc[0] in tables
        if len(loc) == 2:
            key = loc[1]
            with SqliteDict(s.process.filePath, tablename=loc[0], autocommit=True) as db:
                val = db.get(key)
                return val is not None
        elif len(loc) > 2:
            tableName = loc[0]
            key = loc[1]
            with SqliteDict(s.process.filePath, tablename=tableName, autocommit=True) as db:
                vals = db.get(key)
                if vals is None:
                    return False
                s.process.dm.s.process.model = vals
                return s.process.dm.exists(loc[2:])
    def readAll():
        tableNames = s.handlers.get_table_names()
        res = {}
        for t in tableNames:
            res[t] = s.handlers.readTableAsDic(t)
        return res
    def get_table_names():
        return SqliteDict.get_tablenames(s.process.filePath)
    s = ObjMaker.variablesAndFunction(locals())
    s.handlers.s = s
    return s.handlers
