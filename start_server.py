"""Start server"""
import os
import uvicorn

from XAgentServer.application.core.envs import XAgentServerEnv

if __name__ == "__main__":
    os.system("systemctl start nginx")
    uvicorn.run(app="XAgentServer.application.main:app",
                host=XAgentServerEnv.host,
                port=XAgentServerEnv.port,
                reload=XAgentServerEnv.reload,
                workers=XAgentServerEnv.workers)