#!/bin/bash
# find all build.sh files in the sub directories and execute them all
cd `dirname $0`
bash dockerfiles/ToolServerMonitor/build.sh
bash dockerfiles/ToolServerNode/build.sh
bash dockerfiles/ToolServerManager/build.sh