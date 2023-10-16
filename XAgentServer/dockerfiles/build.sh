#!/bin/bash
cd `dirname $0`
docker build -f ./Dockerfile -t xagent-server:0.1 ../../