# %%
from src.domainOpsCrudFastApi import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# # %%
# from src.domainOpsCrud import DomainOpsLoggerCRUD
# dol = DomainOpsLoggerCRUD()
# dol.process.model.readAll()
# # %%
# dol.process.logger.handlers.create("logger1", [], ["c44bee0401c7482fa04c0af6443042a2"], "c44bee0401c7482fa04c0af6443042a2")
# # %%
# dol.process.model.readAll()
# # %%
