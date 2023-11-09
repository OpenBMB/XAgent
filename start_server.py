import uvicorn

from XAgentServer.envs import XAgentServerEnv

if __name__ == "__main__":
    uvicorn.run(
        app="app:app",
        host=XAgentServerEnv.host,
        port=XAgentServerEnv.port,
        reload=XAgentServerEnv.reload,
        workers=XAgentServerEnv.workers,
    )
