docker rmi -f acts
docker build --tag=acts .
docker run -p 80:80 -it -v Db:/app acts
