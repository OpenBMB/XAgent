
import asyncio
import docker.errors
import datetime

from config import CONFIG, logger
from connections import docker_client
from models import ToolServerNode


async def check_nodes_status():
    """
    Check the status of all existing nodes from the selected database 'sqlite3' or 'mongodb'.
    If a node doesn't exist in Docker, it will be deleted from the database. 

    Raises:
        docker.errors.NotFound: Raised when a Node is not found in Docker
        docker.errors.APIError: Raised when it fails to get Node info from Docker
    """
    # Check if each node exists in Docker
    async for node in ToolServerNode.find_all():
        container = None
        try:
            container = docker_client.containers.get(node.id)
        except docker.errors.NotFound:
            # Delete from db if not found in Docker
            await node.delete()
            logger.info("Node deleted from db: " + node.id + '(not in docker)')
            continue
        except docker.errors.APIError:
            logger.warning("Failed to get node info from docker: " + node['node_id'])
            continue

        if container is not None:
            # Update the node state in db
            node_status = container.attrs["State"]["Status"]
 
            if node_status != node.status:
                logger.info(f"Node {node.short_id} status updated: " + node.status + " -> " + node_status)
            node.status = node_status
                
            if CONFIG['node']['health_check']:
                health = container.attrs['State']['Health']['Status']
                if health != node.health:
                    logger.info(f"Node {node.short_id} health updated: " + node.health + " -> " + health)
                node.health = health
                
            await node.replace()

            # Check if node is running
            if node_status == "running":
                if datetime.datetime.utcnow() - node.last_req_time >= datetime.timedelta(minutes=CONFIG['node']['idling_close_minutes']):
                    container.stop()
                    logger.info("Stopping node: " + node.id + " due to idling time used up")


async def check_nodes_status_loop():
    """
    An infinite loop that checks the status of the nodes and waits 1 second before each iteration.
    """
    logger.info("Nodes status checker started.")
    while True:
        try:
            await check_nodes_status()
        except:
            import traceback
            traceback.print_exc()
        await asyncio.sleep(CONFIG['node'].get('health_check_interval',1))


if __name__ == '__main__':
    asyncio.run(check_nodes_status_loop())
