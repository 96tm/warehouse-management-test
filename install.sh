#!/bin/bash
docker volume create StaticVolume
docker volume create DatabaseVolume

docker pull nginx:latest
docker build -t warehouse .

docker run --name web -d \
-e ADD_TEST_DATA=1 \
-e ADMIN_EMAIL=$2 \
-e SERVER_EMAIL=$2 \
-e DEFAULT_FROM_EMAIL=$2 \
-e EMAIL_HOST=$1 \
-e EMAIL_HOST_USER=$2 \
-e EMAIL_HOST_PASSWORD=$3 \
-e CLIENT_EMAIL=$4 \
--volume StaticVolume:/home/warehouse/static \
--volume DatabaseVolume:/home/warehouse/database \
--restart always \
warehouse

docker run --name nginx-custom -d \
-p 8888:80 \
--link web \
--volume StaticVolume:/static \
--volume "$(pwd)"/deployment/conf.d:/etc/nginx/conf.d \
--restart always \
nginx:latest
