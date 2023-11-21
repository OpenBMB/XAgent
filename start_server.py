"""Start server"""
import uvicorn

from XAgentServer.application.core.envs import XAgentServerEnv

if __name__ == "__main__":
    uvicorn.run(app="XAgentServer.application.main:app",
                host=XAgentServerEnv.host,
                port=XAgentServerEnv.port,
                reload=XAgentServerEnv.reload,
                workers=XAgentServerEnv.workers)