docker-compose \
-f docker/compose/docker-compose.rabbitmq.yml \
-f docker/compose/docker-compose.postgres.yml \
-f docker/compose/docker-compose.schema_storage.yml \
-f docker/compose/docker-compose.template_storage.yml \
-f docker/compose/docker-compose.signal.yml \
up --build -d