all: docker

docker:
	docker-compose up --build

clean:
	sudo docker-compose down

fclean:
	sudo docker-compose down -v --rmi all
	docker network prune --force
	docker volume prune --force

format:
	black "./src"