import asyncio
import docker.errors
import datetime

from config import CONFIG, logger
from connections import DB_TYPE, db, docker_client

if DB_TYPE == "sqlite3":
    db_cursor = db.cursor()


async def check_nodes_status():
    # update the status of all nodes in db with info in docker, if node is not in docker, delete it

    if DB_TYPE == "mongodb":
        nodes = db["nodes"].find()
        nodes = [node async for node in nodes]

    if DB_TYPE == "sqlite3":
        db_cursor.execute("SELECT * FROM nodes")
        nodes = db_cursor.fetchall()

        def convert_to_dict(node):
            return {
                "node_id": node[0],
                "node_short_id": node[1],
                "node_status": node[2],
                "node_ip": node[3],
                "node_last_req_time": node[4],
            }

        nodes = list(map(convert_to_dict, nodes))

    for node in nodes:
        # check if node is in docker
        container = None
        try:
            container = docker_client.containers.get(node["node_id"])
        except docker.errors.NotFound:
            # delete node in db
            if DB_TYPE == "sqlite3":
                db_cursor.execute(
                    "DELETE FROM nodes WHERE node_id = ?", (node["node_id"],)
                )
            if DB_TYPE == "mongodb":
                await db["nodes"].delete_one({"node_id": node["node_id"]})
            logger.info("Node deleted from db: " + node["node_id"] + "(not in docker)")
            continue
        except docker.errors.APIError:
            logger.warning("Failed to get node info from docker: " + node["node_id"])
            continue

        if container is not None:
            # update the node state in db
            node_status = container.attrs["State"]["Status"]
            if DB_TYPE == "sqlite3":
                db_cursor.execute(
                    "UPDATE nodes SET node_status = ? WHERE node_id = ?",
                    (node_status, node["node_id"]),
                )
                if CONFIG["node"]["health_check"]:
                    db_cursor.execute(
                        "UPDATE nodes SET node_health = ? WHERE node_id = ?",
                        (container.attrs["State"]["Health"]["Status"], node["node_id"]),
                    )
            if DB_TYPE == "mongodb":
                await db["nodes"].update_one(
                    {"node_id": node["node_id"]}, {"$set": {"node_status": node_status}}
                )
                if CONFIG["node"]["health_check"]:
                    await db["nodes"].update_one(
                        {"node_id": node["node_id"]},
                        {
                            "$set": {
                                "node_health": container.attrs["State"]["Health"][
                                    "Status"
                                ]
                            }
                        },
                    )

            # check if node is running
            if node_status == "running":
                last_req_time = datetime.datetime.fromisoformat(
                    node["node_last_req_time"]
                )
                if datetime.datetime.utcnow() - last_req_time >= datetime.timedelta(
                    minutes=CONFIG["node"]["idling_close_minutes"]
                ):
                    container.stop()
                    logger.info(
                        "Stopping node: "
                        + node["node_id"]
                        + "  due to idling time used up"
                    )

    if DB_TYPE == "sqlite3":
        db.commit()


async def check_nodes_status_loop():
    while True:
        await check_nodes_status()
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(check_nodes_status_loop())
