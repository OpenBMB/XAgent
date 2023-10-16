#!/bin/bash
cd `dirname $0`
docker build -f ./Dockerfile -t tool-server-monitor:0.1 ../../