import aio_pika
from aio_pika import Message


async def job_send_message(
    					amqp_url: str,
						exchange_name: str,
						body: bytes,
						routing_key: str
    ):
	amqp_connection = await aio_pika.connect_robust(amqp_url)
	
	async with amqp_connection:
		amqp_channel = await amqp_connection.channel()
		exchange = await amqp_channel.get_exchange(exchange_name)
		await exchange.publish(
			message=Message(
				body=body,
			),
			routing_key=routing_key
		)
	await amqp_connection.close()
	return

