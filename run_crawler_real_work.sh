docker-compose \
-f docker/compose/docker-compose.scheduler.yml \
-f docker/compose/docker-compose.rabbitmq.yml \
-f docker/compose/docker-compose.mongodb.yml \
-f docker/compose/docker-compose.postgres.yml \
-f docker/compose/docker-compose.schema_storage.yml \
-f docker/compose/docker-compose.template_storage.yml \
-f docker/compose/docker-compose.nginx.yml \
-f docker/compose/docker-compose.spider.yml \
-f docker/compose/docker-compose.item_storage.yml \
up --build -d