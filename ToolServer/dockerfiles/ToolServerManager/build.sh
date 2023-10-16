#!/bin/bash
cd `dirname $0`
docker build -f ./Dockerfile -t tool-server-manager:0.2 ../../