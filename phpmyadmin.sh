docker rm -f Electric-Measurement
docker run --restart=always --name Electric-Measurement -d -e PMA_HOST=192.168.0.120 -p 8088:80 phpmyadmin/phpmyadmin
