import json

import pika

credentials = pika.PlainCredentials('admin', 'admin')
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672, '/', credentials))


def send_email(payload):
    channel = connection.channel()
    channel.queue_declare(queue='email_queue')
    channel.basic_publish(exchange='', routing_key='email_queue', body=json.dumps(payload))
