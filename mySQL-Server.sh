docker rm -f Electric-Measurement
docker run -d --restart=always --name Electric-Measurement -p 3306:3306 -v /volume1/docker/mysqldata:/var/lib/mysql -e MYSQL_ROOT_PASSWORD=Solenoide -e MYSQL_DATABASE=Electric-Measurement mysql --default-authentication-plugin=mysql_native_password --skip-mysqlx
