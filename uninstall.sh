#!/bin/bash
docker stop nginx-custom
docker stop web
docker rm nginx-custom
docker rm web
docker image rm -f warehouse
docker volume rm StaticVolume
docker volume rm DatabaseVolume
