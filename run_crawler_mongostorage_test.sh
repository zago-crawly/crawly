docker-compose \
-f docker/compose/docker-compose.rabbitmq.yml \
-f docker/compose/docker-compose.mongodb.yml \
-f docker/compose/docker-compose.mongostorage.yml \
up --build -d