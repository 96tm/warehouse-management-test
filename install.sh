#!/bin/bash
docker volume create StaticVolume
docker volume create DatabaseVolume

docker pull nginx:latest
docker build -t warehouse .

docker run --name web -d \
-e ADD_TEST_DATA=1 \
-e ADMIN_EMAIL=den_se_in@mail.ru \
-e SERVER_EMAIL=den_se_in@mail.ru \
-e DEFAULT_FROM_EMAIL=den_se_in@mail.ru \
-e EMAIL_HOST=smtp.mail.ru \
-e EMAIL_HOST_USER=den_se_in@mail.ru \
-e EMAIL_HOST_PASSWORD="/9WGF\\v;]}" \
-e CLIENT_EMAIL=den_se_in@mail.ru \
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
