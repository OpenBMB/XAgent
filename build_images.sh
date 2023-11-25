#/bin/bash
docker buildx build --push --platform linux/arm64,linux/amd64 -t xagentteam/toolserver-manager:0.2 -f dockerfiles/ToolServerManager/Dockerfile .
docker buildx build --push --platform linux/arm64,linux/amd64 -t xagentteam/toolserver-manager -f dockerfiles/ToolServerManager/Dockerfile .
docker buildx build --push --platform linux/arm64,linux/amd64 -t xagentteam/toolserver-node:0.2 -f dockerfiles/ToolServerNode/Dockerfile .
docker buildx build --push --platform linux/arm64,linux/amd64 -t xagentteam/toolserver-node -f dockerfiles/ToolServerNode/Dockerfile .
docker buildx build --push --platform linux/arm64,linux/amd64 -t xagentteam/xagent-server:0.3 -f dockerfiles/XAgentServer/Dockerfile .
docker buildx build --push --platform linux/arm64,linux/amd64 -t xagentteam/xagent-server -f dockerfiles/XAgentServer/Dockerfile .

docker buildx build --push --platform linux/amd64 -t xagentteam/xagentgen:0.1 -f dockerfiles/XAgentGen/Dockerfile .
docker buildx build --push --platform linux/amd64 -t xagentteam/xagentgen -f dockerfiles/XAgentGen/Dockerfile .