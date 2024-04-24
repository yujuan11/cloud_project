## readme file to show how to use this repository.
# 1: Dependancys:
Create three virtual machines using .iso baseOS image file. 

Here I used rocky9.3 mininal: https://www.ole.bris.ac.uk/ultra/courses/_254903_1/cl/outline

Install docker on all machines. Create ont virtual machine and install docker, then clone twice.

`sudo usermod -aG docker user1` # add docker to sudo group

# 2: Create a swarm with three nodes inside
Open the port 2377 for docker communication, port 7946 for node discovery, and port 4789 for network traffic
     
`sudo firewall-cmd --zone=public --add-port=2377/tcp --permanent`

`sudo firewall-cmd --zone=public --add-port=7946/tcp --permanent`

`sudo firewall-cmd --zone=public --add-port=4789/udp --permanent`

`sudo firewall-cmd --reload`

`docker swarm init --advertise-addr 192.168.241.3`  # initialise a swarm manager

`docker swarm join --token SWMTKN-1-49vxwsf4zmw8ntvfcpnmr7hrns636tjol61291verzym8h48h5-ekb5gi6yqft1owxeg3g0rwe0l 192.168.241.3:2377`  # join a new node as a worker 

 `docker swarm join --token SWMTKN-1-49vxwsf4zmw8ntvfcpnmr7hrns636tjol61291verzym8h48h5-5mb8h6cru86ajpt5f2xoi3w2u 192.168.241.3:2377` # join a new node as a manager


Here is the documentation about how to create a swarm and add new node :
https://docs.docker.com/engine/swarm/swarm-tutorial/


# 3: Deploy service on the docker swarm by using docker-compose.yml file: 

`docker run -d -p 5000:5000 -v my_registry:/var/lib/registry --name registry registry:latest` # run registry

`docker build -t rpimage .` # build the images and tag them

`docker build -t proimage .`

`docker build -t plotimage .`

`docker tag rpimage localhost:5000/my_rpimage`

`docker tag rpimage localhost:5000/my_proimage`

`docker tag rpimage localhost:5000/my_plotimage`

`docker tag rabbitmq localhost:5000/my_plotimage`

`docker push localhost:5000/my_rpimage`

``

``

``

``





