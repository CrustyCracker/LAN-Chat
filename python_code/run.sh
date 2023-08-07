#!/bin/sh
docker rm ui
docker build -t ui .
docker run -it --network bridge ui
