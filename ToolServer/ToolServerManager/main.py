import uvicorn
import httpx
import sqlite3
import asyncio
import traceback
import datetime
import docker.types

from fastapi import FastAPI, Cookie, Request, HTTPException, Response
from fastapi.responses import JSONResponse, RedirectResponse

from config import CONFIG, logger
from connections import DB_TYPE, db, docker_client

app = FastAPI()


@app.on_event("startup")
async def startup():
    if DB_TYPE == "sqlite3":
        # check if table nodes exists
        db_cursor: sqlite3.Cursor = db.cursor()
        db_cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='nodes'"
        )
        if db_cursor.fetchone() is None:
            db_cursor.execute(
                "CREATE TABLE nodes (node_id text, node_short_id text, node_status text, node_ip text, node_last_req_time text,node_health text)"
            )
            db.commit()
            logger.info("Table nodes created")
        app.db_cursor = db_cursor

    # create subprocess to update node status
    if CONFIG["builtin_monitor"]:
        from node_checker import check_nodes_status_loop

        asyncio.create_task(check_nodes_status_loop())

    # register path to node
    for path in CONFIG["redirect_to_node_path"]["post"]:
        app.add_api_route(path, route_to_node, methods=["POST"])

    for path in CONFIG["redirect_to_node_path"]["get"]:
        app.add_api_route(path, route_to_node, methods=["GET"])


@app.on_event("shutdown")
def shutdown():
    if DB_TYPE == "sqlite3":
        app.db_cursor.close()


@app.get("/alive")
async def alive():
    return "alive"


async def get_node_info(node_id: str):
    # check if cookie is valid
    if DB_TYPE == "sqlite3":
        db_cursor: sqlite3.Cursor = app.db_cursor
        db_cursor.execute("SELECT * FROM nodes WHERE node_id = ?", (node_id,))
        node = db_cursor.fetchone()
        if node is not None:
            node = {
                "node_id": node[0],
                "node_short_id": node[1],
                "node_status": node[2],
                "node_ip": node[3],
                "node_last_req_time": node[4],
                "node_health": node[5],
            }
    if DB_TYPE == "mongodb":
        node = await db["nodes"].find_one({"node_id": node_id})
    return node


async def wait_for_node_startup(node_id: str):
    MAX_PROBE_TIMES = CONFIG["node"]["creation_wait_seconds"]
    probe_times = 0
    while probe_times < MAX_PROBE_TIMES:
        node = await get_node_info(node_id)

        if node is None:
            raise HTTPException(
                status_code=503,
                detail="Failed to detect node status! Node not found in db!",
            )

        if CONFIG["node"]["health_check"]:
            if node["node_health"] == "healthy":
                return True
        else:
            if node["node_status"] == "running":
                return True

        probe_times += 1
        await asyncio.sleep(1)
    return False


@app.post("/get_cookie")
async def read_cookie_info():
    # append server version info
    content = {"message": "add cookie", "version": CONFIG["version"]}
    response = JSONResponse(content=content)
    response.headers["Server"] = "ToolServerManager/" + CONFIG["version"]

    # create a docker container
    container = docker_client.containers.run(
        device_requests=[
            docker.types.DeviceRequest(**req)
            for req in CONFIG["node"]["device_requests"]
        ]
        if CONFIG["node"]["device_requests"]
        else None,
        **(CONFIG["node"]["creation_kwargs"]),
    )
    logger.info("Node created: " + container.id)
    response.set_cookie(key="node_id", value=container.id)
    container.reload()
    if DB_TYPE == "sqlite3":
        db_cursor: sqlite3.Cursor = app.db_cursor
        # add node to db
        db_cursor.execute(
            "INSERT INTO nodes (node_id,node_short_id,node_status,node_ip,node_last_req_time,node_health) VALUES (?, ?, ?, ?, ?, ?)",
            (
                container.id,
                container.short_id,
                container.attrs["State"]["Status"],
                container.attrs["NetworkSettings"]["Networks"][
                    CONFIG["node"]["creation_kwargs"]["network"]
                ]["IPAddress"],
                datetime.datetime.utcnow().isoformat(),
            ),
            container.attrs["State"]["Health"]["Status"],
        )
        db.commit()
    if DB_TYPE == "mongodb":
        logger.debug(container.attrs["State"])
        await db["nodes"].insert_one(
            {
                "node_id": container.id,
                "node_short_id": container.short_id,
                "node_status": container.attrs["State"]["Status"],
                "node_ip": container.attrs["NetworkSettings"]["Networks"][
                    CONFIG["node"]["creation_kwargs"]["network"]
                ]["IPAddress"],
                "node_last_req_time": datetime.datetime.utcnow().isoformat(),
                "node_health": container.attrs["State"]["Health"]["Status"],
            }
        )

    # probe node status every seconds until creation_wait_seconds reached
    if await wait_for_node_startup(container.id):
        return response
    else:
        logger.warning("Node status detection timeout: " + container.id)
        raise HTTPException(status_code=503, detail="Node creation timeout!")


@app.post("/reconnect_session")
async def reconnect_session(node_id: str = Cookie(None)):
    node = await get_node_info(node_id)
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
async def close_session(node_id: str = Cookie(None)):
    node = await get_node_info(node_id)
    if node is None:
        return "invalid node_id: " + str(node_id)
    # stop node
    container = docker_client.containers.get(node_id)
    if container is not None and container.attrs["State"]["Status"] != "exit":
        container.stop()
        logger.info("Node stopped: " + node_id)
    return "Close session: " + str(node_id)


@app.post("/release_session")
async def release_session(node_id: str = Cookie(None)):
    node = await get_node_info(node_id)
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


async def route_to_node(requset: Request, *, node_id: str = Cookie(None)):
    # logger.info("accept node_id:",node_id)
    node = await get_node_info(node_id)
    if node is None:
        raise HTTPException(status_code=403, detail="invalid node_id: " + str(node_id))

    if node["node_status"] != "running":
        raise HTTPException(
            status_code=503, detail="node is not running: " + str(node_id)
        )

    # update latest_req_time in db
    if DB_TYPE == "sqlite3":
        app.db_cursor.execute(
            "UPDATE nodes SET node_last_req_time = ? WHERE node_id = ?",
            (datetime.datetime.utcnow().isoformat(), node_id),
        )
        db.commit()
    if DB_TYPE == "mongodb":
        await db["nodes"].update_one(
            {"node_id": node_id},
            {"$set": {"node_last_req_time": datetime.datetime.utcnow().isoformat()}},
        )

    # post request to node
    method = requset.method
    headers = dict(requset.headers)
    body = await requset.body()
    url = "http://" + node["node_ip"] + ":31942" + requset.url.path
    logger.info("Request to node: " + url)

    async with httpx.AsyncClient(timeout=None) as client:
        try:
            response = await client.request(method, url, headers=headers, data=body)
        except httpx.RequestError:
            traceback.print_exc()
            raise HTTPException(status_code=503, detail="node is not responding")
    logger.info("Response from node: " + str(response.status_code))
    res = Response(
        content=response.content,
        status_code=response.status_code,
        headers=response.headers,
    )
    return res


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
