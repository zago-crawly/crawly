docker-compose \
-f docker/compose/docker-compose.nginx.yml \
-f docker/compose/docker-compose.postgres.yml \
-f docker/compose/docker-compose.schema_storage.yml \
-f docker/compose/docker-compose.rabbitmq.yml \
up --build -d