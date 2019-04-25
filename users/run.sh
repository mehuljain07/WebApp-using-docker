docker rmi -f users
docker build --tag=users .
docker run -p 8080:80 -it -v /home/ubuntu/users/:/app users
