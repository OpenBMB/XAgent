#!/bin/bash
cd `dirname $0`
docker build -f ./Dockerfile -t tool-server-node:0.2 ../../ 