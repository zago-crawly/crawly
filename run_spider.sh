docker-compose \
-f docker/compose/docker-compose.scheduler.yml \
-f docker/compose/docker-compose.rabbitmq.yml \
-f docker/compose/docker-compose.mongodb.yml \
-f docker/compose/docker-compose.nginx.yml \
-f docker/compose/docker-compose.spider.yml \
up --build -d