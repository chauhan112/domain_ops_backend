from .dbModel import ObjMaker, SqliteModelV3
from LibPath import insertPath
insertPath()
from CryptsDB import CryptsDB

def GenericCategory():
    category = "domains"
    model = None
    NAME = "name"
    PROP = "properties"
    def create(name, loc):
        idd = CryptsDB.generateUniqueId()
        s.process.model.add(loc + [s.process.category,idd], {NAME: name, "id": idd} )
        return idd
    def delete(idd, loc):
        s.process.model.delete(loc + [s.process.category, idd] )
    def readAll(loc):
        vals = s.process.model.read(loc +[s.process.category])
        return list(map(lambda x: (x, vals[x][NAME]), vals))
    def update(newName, idd, loc):
        s.process.model.add(loc + [s.process.category, idd], {NAME: newName} )
    def read(idd, loc):
        return s.process.model.read(loc + [s.process.category, idd])
    def exists(idd, loc):
        return s.process.model.exists(loc + [s.process.category, idd])
    def nameExists(name, loc):
        vals = s.process.model.read(loc +[s.process.category])
        for key in vals:
            if vals[key][NAME] == name:
                return True
        return False
    def readProperties(idd, loc):
        if not s.process.model.exists(loc + [s.process.category, idd, PROP]):
            s.process.model.add(loc + [s.process.category, idd, PROP], {})
            return {}
        return s.process.model.read(loc + [s.process.category, idd, PROP])
    def addNewProperty(idd, loc, key, value):
        s.process.model.add(loc + [s.process.category, idd, PROP, key], value)
    def deleteProperty(idd, loc, key):
        s.process.model.delete(loc + [s.process.category, idd, PROP, key])
    def updateProperty(idd, loc, key, value):
        newLoc = loc + [s.process.category, idd, PROP, key]
        if s.process.model.exists(newLoc):
            s.process.model.add(newLoc, value)
    def existsProperty(idd, loc, key):
        newLoc = loc + [s.process.category, idd, PROP, key]
        return s.process.model.exists(newLoc)
    s = ObjMaker.variablesAndFunction(locals())
    return s
def DomainOpsLoggerCRUD():
    domains = GenericCategory()
    operations = GenericCategory()
    logger = GenericCategory()
    domains.process.category = "domains"
    operations.process.category = "operations"
    logger.process.category = "logger"
    model = SqliteModelV3()
    domains.process.model = model
    operations.process.model = model
    logger.process.model = model
    model.s.process.filePath = "db.sqlite"
    def set_path(path):
        s.process.model.s.process.filePath = path
    def create_logger(name, loc, doms, opId):
        if len(doms) == 0:
            raise Exception("Domains cannot be empty")
        cat = s.process.logger.process.category
        NAME = s.process.logger.process.NAME
        OPERATION = "operation"
        DOMAINS = "domains"
        idd = CryptsDB.generateUniqueId()
        s.process.model.add(loc + [cat, idd], 
            {NAME: name, OPERATION: opId, DOMAINS: doms, "id": idd} )
        return idd
    def update_logger(idd, loc, name=None, doms=None, opId=None):
        if name is None and doms is None and opId is None:
            return
        
        cat = s.process.logger.process.category
        NAME = s.process.logger.process.NAME
        OPERATION = "operation"
        DOMAINS = "domains"
        data = s.process.model.read(loc + [cat, idd])
        
        if len(data["domains"]) == 0 and doms is None:
            raise ValueError("Domains cannot be empty")
        if opId is None and data[OPERATION] is None:
            raise ValueError("Operations cannot be empty")
        if name is not None:
            data[NAME] = name
        if doms is not None:
            data[DOMAINS] = doms
        if opId is not None:
            data[OPERATION] = opId
        s.process.model.add(loc + [cat, idd], data )
    logger.handlers.update = update_logger
    logger.handlers.create = create_logger
    s = ObjMaker.variablesAndFunction(locals())
    return s