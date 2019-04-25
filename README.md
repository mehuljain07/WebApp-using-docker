# WebApp-using-docker
Implements a Web Application using docker, flask and REST API

Instance-1
Load Balancer run in built-in Flask Server on port 80 (Needs to be give permission and stop all other services.
Acts running in docker on port (8000 and above). Image-ccdocker1/acts:latest

Instance-2
Users app running on docker container(on port 80) in instance-2.
Image- ccdocker1/users:latest
