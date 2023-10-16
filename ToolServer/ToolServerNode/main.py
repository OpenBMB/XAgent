import os
import sys
import zipfile
import traceback

from typing import Coroutine,List

from fastapi import FastAPI,Body,UploadFile
from fastapi.requests import Request
from fastapi.exceptions import HTTPException
from starlette.responses import FileResponse

from config import CONFIG,logger
from core.register import ToolRegister
from core.exceptions import ToolNotFound,OutputNotReady

from utils.retriever import ada_retriever,build_tool_embeddings
from utils.response import wrap_tool_response

app = FastAPI()

@app.on_event("startup")
def startup():
    try:
        # start docker service
        os.system('service docker start')
    except:
        pass
    app.tool_register = ToolRegister()
    app.doc_embeddings, app.id2tool = build_tool_embeddings(app.tool_register.get_all_tools_dict(include_invisible=True))

@app.post("/")
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post('/upload_file')
async def upload_file(file:UploadFile):
    upload_file =  file.file.read()
    file_name = file.filename
    work_directory = CONFIG['filesystem']['work_directory']
    with open(os.path.join(work_directory,file_name),'wb') as f:
        f.write(upload_file)
    return {"message": "Upload Success!"}

@app.post('/download_file')
async def download_file(file_path:str=Body(...),file_type:str=Body(default='text/plain')):
    work_directory = CONFIG['filesystem']['work_directory']
    if file_path.startswith(os.path.basename(work_directory)):
        file_path = file_path[len(os.path.basename(work_directory))+1:]
    response = FileResponse(
        path=os.path.join(work_directory,file_path),
        filename=os.path.basename(file_path),
        )
    return response
@app.post('/download_workspace')
async def download_workspace():
    work_directory = CONFIG['filesystem']['work_directory']
    zip = zipfile.ZipFile('/tmp/workspace.zip','w',zipfile.ZIP_DEFLATED)
    for path,dirs,files in os.walk(work_directory):
        fpath= path.replace(work_directory,'')
        for file in files:
            zip.write(os.path.join(path,file),os.path.join(fpath,file))
    
    zip.close()
    response = FileResponse(
        path=os.path.join(work_directory,'/tmp/workspace.zip'),
        filename='workspace.zip',
        )
    return response


@app.post('/get_workspace_structure')
async def get_workspace_structure():
    work_directory = CONFIG['filesystem']['work_directory']
    def generate_directory_structure(path):
        result = {'name':os.path.basename(path)}
        if os.path.isdir(path):
            result['type'] = 'directory'
            result['children'] = [generate_directory_structure(os.path.join(path,child)) for child in os.listdir(path)]
        else:
            result['type'] = 'file'
        return result
    return generate_directory_structure(work_directory)

@app.post('/get_available_tools')
async def get_available_tools():
    tool_register:ToolRegister = app.tool_register
    return {
        "available_envs": tool_register.get_all_envs(),
        "available_tools": tool_register.get_all_tools(),
        "tools_json": tool_register.get_all_tools_dict(),
    }


@app.post('/retrieving_tools')
async def retrieving_tools(question:str=Body(...), top_k:int=Body(default=5)):
    try:
        retrieved_tools = ada_retriever(app.doc_embeddings, app.id2tool, question, top_k)
    except Exception as e:
        error_report =  traceback.format_exc()
        logger.error(error_report)
        raise HTTPException(status_code=500, detail=f"Errorhappens when retrieving tools:\n{e}\n\n" + error_report)
    
    tool_register:ToolRegister = app.tool_register
    tools_json = []
    for tool_name in retrieved_tools:
        if tool_name in tool_register.tools:
            tools_json.append(tool_register.get_tool_dict(tool_name))
    
    return {
        "retrieved_tools":retrieved_tools,
        "tools_json":tools_json,
    }
    

@app.post('/get_json_schema_for_tools')
async def get_json_schema_for_tool(tool_names:List[str]=Body(...)):
    tool_register:ToolRegister = app.tool_register
    
    error_names = []
    tools_json = []
    for tool_name in tool_names:
        if tool_name not in tool_register.tools:
            error_names.append(tool_name)
        else:
            tools_json.append(tool_register.get_tool_dict(tool_name))
    return {
        "tools_json": tools_json,
        "missing_tools": error_names,
    }

@app.post('/get_json_schema_for_envs')
async def get_json_schema_for_env(env_names:List[str]=Body(...)):
    tool_register:ToolRegister = app.tool_register
    
    error_names = []
    envs_json = []
    for env_name in env_names:
        if env_name not in tool_register.envs:
            error_names.append(env_name)
        else:
            envs_json.append(tool_register.get_env_dict(env_name))
    return {
        "envs_json": envs_json,
        "missing_envs": error_names,
    }
    
@app.post('/register_new_tool')
async def register_new_tool(tool_name:str=Body(...), code:str=Body(...)):
    tool_register:ToolRegister = app.tool_register
    try:
        tool_dict = tool_register.register_tool(tool_name,code)
    except Exception as e:
        error_report =  traceback.format_exc()
        logger.error(error_report)
        raise HTTPException(status_code=406, detail=f"Error happens when registering new tool:\n{e}\n\n" + error_report)
    
    return tool_dict


@app.post('/execute_tool')
async def execute_tool(tool_name:str=Body(...), arguments:dict=Body(...), env_name:str=Body(default=None)):
    tool_register:ToolRegister = app.tool_register
    
    try:
        if env_name is not None:
            tool = tool_register[env_name,tool_name]
        else:
            tool = tool_register[tool_name]
        result = tool(**arguments)
        if isinstance(result,Coroutine):
            result = await result
        result = wrap_tool_response(result)
    except ToolNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except OutputNotReady as e:
        raise HTTPException(status_code=450, detail=e.next_try())
    except HTTPException as e:
        raise e
    except Exception as e:
        trace_info = traceback.format_exc()
        logger.error(f'Error happens when executing tool {tool_name}! Exception: {e}\n{trace_info}')
        raise HTTPException(status_code=500, detail=trace_info)
    
    return result

if __name__=='__main__':
    import uvicorn
    uvicorn.run(app, port=12345)