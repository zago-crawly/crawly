import aio_pika
from aio_pika import Message
import asyncio
import json


def job_send_message(
    					amqp_url: str,
						exchange_name: str,
						body: dict,
						routing_key: str
    ):
	return asyncio.run(_async_job_send_message(amqp_url, exchange_name, body, routing_key))

async def _async_job_send_message(
    					amqp_url: str,
						exchange_name: str,
						body: dict,
						routing_key: str
    ):
	amqp_connection = await aio_pika.connect_robust(amqp_url)
	async with amqp_connection:
		amqp_channel = await amqp_connection.channel()
		exchange = await amqp_channel.get_exchange(exchange_name)
		json_body = json.dumps(body, ensure_ascii=False).encode()
		print(json_body)
		await exchange.publish(
			message=Message(
				body=json_body,
			),
			routing_key=routing_key
		)
	await amqp_connection.close()
	return