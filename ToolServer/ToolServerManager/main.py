import os
import psutil
import uvicorn
import httpx
import asyncio
import traceback
import datetime
import docker.types

from fastapi import FastAPI, Cookie,Request,HTTPException,Response
from fastapi.responses import JSONResponse,RedirectResponse
from config import CONFIG,logger,MANAGER_ID
from connections import db,docker_client
from models import ToolServerNode, NodeChecker

app = FastAPI()

@app.on_event("startup")
async def startup():
    """
    Event handler triggered on startup of the app. Sets up necessary configurations 
    like checking and creating table nodes if not exists in databse, creating subprocess 
    to update node status, and registering path to node. 
    """
    
    from beanie import init_beanie
    await init_beanie(database=db,
                      document_models=[ToolServerNode,NodeChecker],)
    
    # create subprocess to update node status
    if CONFIG['builtin_monitor']:
        from node_checker import check_nodes_status_loop
        
        async for checker in NodeChecker.find_all():
            if not psutil.pid_exists(checker.pid):
                checker.delete()

        checker = NodeChecker(
            manager_id=MANAGER_ID,
            interval=float(CONFIG['node'].get('health_check_interval',1)),
            pid=os.getpid()
            )
        await checker.save()

        asyncio.create_task(check_nodes_status_loop())
            

    # register path to node
    for path in CONFIG['redirect_to_node_path']['post']:
        app.add_api_route(path, route_to_node, methods=["POST"])
        
    for path in CONFIG['redirect_to_node_path']['get']:
        app.add_api_route(path, route_to_node, methods=["GET"])

@app.on_event("shutdown")
async def shutdown():
    """
    Event handler on shutdown of the app. Specifically closes the database cursor if 
    the database type os sqlite3.
    """
    async for checker in NodeChecker.find(NodeChecker.manager_id == MANAGER_ID):
        await checker.delete()
    db.client.close()
        
@app.get('/alive')
async def alive():
    """
    Endpoint to check if the service is running.

    Returns:
        str: "alive"
    """
    return "alive"

async def wait_for_node_startup(node_id:str):
    """
    Wait for the startup of node with id node_id. It probes the node status every seconds until 
    creation_wait_seconds reached.
    
    Args:
        node_id (str): The unique identifier of the node whose startup is to be waited for.

    Returns:
        bool: True if node has started successfully, False if time out occured before node startup.
    
    Raises:
        HTTPException: If node is not found in the databse.
    """
    MAX_PROBE_TIMES = CONFIG['node']['creation_wait_seconds']
    probe_times = 0
    while probe_times < MAX_PROBE_TIMES:
        node = await ToolServerNode.find_one(ToolServerNode.id == node_id)
            
        if node is None:
            raise HTTPException(status_code=503, detail="Failed to detect node status! Node not found in db!")
        
        if CONFIG['node']['health_check']:
            if node.health == 'healthy':
                return True
        else:
            if node.status == "running":
                return True
            
        probe_times += 1
        await asyncio.sleep(1)
    return False

@app.post("/get_cookie")
async def read_cookie_info():
    """
    Fetch server version and node info, create docker container and set the response cookies 
    with the key "node_id" and value as the id of the created container. Also, adds the created 
    node's details to the databse and waits for the node to startup.

    Returns:
        JSONResponse: A response object with status, headers and cookies set accordingly.

    Raises:
        HTTPException: If node creation timeout occurs.
    """
    # append server version info
    content = {"message": "add cookie","version":CONFIG['version']}
    response = JSONResponse(content=content)
    response.headers["Server"] = "ToolServerManager/" + CONFIG['version']
    
    # create a docker container
    container = docker_client.containers.run(
        device_requests=[docker.types.DeviceRequest(**req) for req in CONFIG['node']['device_requests']] if CONFIG['node']['device_requests'] else None,
        **(CONFIG['node']['creation_kwargs']),)
    logger.info("Node created: " + container.id)
    response.set_cookie(key="node_id", value=container.id)
    container.reload()
    
    node = ToolServerNode(
        id=container.id,
        short_id=container.short_id,
        status=container.attrs["State"]["Status"],
        ip=container.attrs["NetworkSettings"]["Networks"][CONFIG['node']['creation_kwargs']['network']]["IPAddress"],
        port=CONFIG['node'].get('port',31942),
        last_req_time=datetime.datetime.utcnow(),
        health=container.attrs['State']['Health']['Status'] if CONFIG['node']['health_check'] else None
    )
    await node.insert()

    # probe node status every seconds until creation_wait_seconds reached
    if await wait_for_node_startup(container.id):
        return response
    else:
        logger.warning("Node status detection timeout: " + container.id)
        raise HTTPException(status_code=503, detail="Node creation timeout!")

@app.post("/reconnect_session")
async def reconnect_session(node_id:str = Cookie(None)):
    """
    Reconnect session of a node. Fetches node info and restarts the node if it exists.

    Args:
        node_id (str, optional): The unique identifier of the node. Defaults to Cookie(None).

    Returns:
        str: Success message if node restarts successfully.
    
    Raises:
        HTTPException: If node restart timeout occurs.
    """
    node = await ToolServerNode.find_one(ToolServerNode.id == node_id)
    if node is None:
        return "invalid node_id: " + str(node_id)
    # restart node
    container = docker_client.containers.get(node_id)
    if container is not None:
        container.restart()
        logger.info("Node restarted: " + node_id)
    
    if await wait_for_node_startup(node_id):
        return "Reconnect session: " + str(node_id)
    else:
        logger.warning("Node restart timeout: " + node_id)
        raise HTTPException(status_code=503, detail="Node restart timeout!")

@app.post("/close_session")
async def close_session(node_id:str = Cookie(None)):
    """
    Close session of a node. Fetches node info and stops the node if it exists and is not already exited.

    Args:
        node_id (str, optional): The unique identifier of the node. Defaults to Cookie(None).

    Returns:
        str: Success message if node stops successfully.
    """
    node = await ToolServerNode.find_one(ToolServerNode.id == node_id)
    if node is None:
        return "invalid node_id: " + str(node_id)
    # stop node
    container = docker_client.containers.get(node_id)
    if container is not None and container.attrs["State"]["Status"] != "exit":
        container.stop()
        logger.info("Node stopped: " + node_id)
    return "Close session: " + str(node_id)

@app.post("/release_session")
async def release_session(node_id:str = Cookie(None)):
    """
    Release session of a node. Fetches node info and kills the node if it exists and is not already exited. 
    Also, removes the node.

    Args:
        node_id (str, optional): The unique identifier of the node. Defaults to Cookie(None).

    Returns:
        str: Success message if node is successfully killed and removed.
    """
    node = await ToolServerNode.find_one(ToolServerNode.id == node_id)
    if node is None:
        return "invalid node_id: " + str(node_id)
    
    # delete node in docker
    container = docker_client.containers.get(node_id)
    if container is not None:
        if container.attrs["State"]["Status"] != "exited":
            container.kill()
            logger.info("Node killed: " + node_id)
        container.remove()
        logger.info("Node deleted: " + node_id)
    return "Release session: " + str(node_id)

async def route_to_node(requset:Request,*,node_id:str = Cookie(None)):
    """
    Routes a request to a specific node. Fetches the node info, checks if it is valid and running. Updates latest 
    request time in the database and then sends a post request to the node.
    
    Args:
        request (Request): The request object containing all request information.

    Returns:
        Response: The response object containing all response information received from the node.

    Raises:
        HTTPException: If node_id is not valid or if the node is not running or not responding.
    """
    # logger.info("accept node_id:",node_id)
    node = await ToolServerNode.find_one(ToolServerNode.id == node_id)
    if node is None:
        raise HTTPException(status_code=403,detail="invalid node_id: " + str(node_id)) 
    
    if node.status != "running":
        raise HTTPException(status_code=503,detail="node is not running: " + str(node_id)) 

    # update latest_req_time in db
    node.last_req_time = datetime.datetime.utcnow()
    await node.replace()
        
    #post request to node
    method = requset.method
    headers = dict(requset.headers)
    body = await requset.body()
    url = "http://" + node.ip +":"+str(node.port) + requset.url.path
    logger.info("Request to node: " + url)
    
    async with httpx.AsyncClient(timeout=None) as client:
        try:
            response = await client.request(method,url,headers=headers,data=body)
        except httpx.RequestError:
            traceback.print_exc()
            raise HTTPException(status_code=503, detail="node is not responding")
    logger.info('Response from node: ' + str(response.status_code))
    res = Response(content=response.content, status_code=response.status_code, headers=response.headers)
    return res

if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)