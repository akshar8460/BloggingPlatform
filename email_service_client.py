import json

import pika

from config import *

credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_SERVER, RABBITMQ_PORT, '/', credentials))


def send_email(payload):
    channel = connection.channel()
    channel.queue_declare(queue='email_queue')
    channel.basic_publish(exchange='', routing_key='email_queue', body=json.dumps(payload))
