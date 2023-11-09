import uvicorn
from XAgentServer.envs import XAgentServerEnv

if __name__ == "__main__":
    """
    Main execution method for running the server when the script is run directly,
    rather than through an import statement.
    Uses the Uvicorn ASGI server to serve the FastAPI application declared elsewhere in the script,
    with host, port, server reload settings, and number of workers defined in environment settings
    from XAgentServer.envs.XAgentServerEnv.
    """
    uvicorn.run(app="app:app", host=XAgentServerEnv.host,
                port=XAgentServerEnv.port, reload=XAgentServerEnv.reload, workers=XAgentServerEnv.workers)