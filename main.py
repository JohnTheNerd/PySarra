import os
import sys
import time
import re
import ssl
import json
import importlib
import logging
import random
import string
import threading
import pika

sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), 'processors'))

log_format = ('%(asctime)s - %(levelname)s - %(name)s - %(funcName)s: %(message)s')
logging.basicConfig(level='INFO', format=log_format)

class ECConsumer(object):
    exchange = 'xpublic'
    exchange_type = 'topic'
    queue = 'q_anonymous_PySarra_'
    for i in range(0, 12):
        queue = queue + random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits)

    def __init__(self, task):
        self.task = task
        self.routing_key = 'v02.post.'
        self.topic = None
        self.regex = None
        if 'topic' in task:
            if task['topic']:
                if not task['topic'].startswith('*.WXO-DD.'):
                    task['topic'] = '*.WXO-DD.' + task['topic']
                self.routing_key = self.routing_key + str(task['topic']) + '.'
                self.topic = task['topic']
                self.routing_key = self.routing_key + '#'
        if 'regex' in task:
            if task['regex']:
                self.regex = re.compile(task['regex'])
        self.processor = importlib.import_module(task['processor'])

    def connect(self):
        credentials = pika.PlainCredentials('anonymous', 'anonymous')
        context = ssl.create_default_context()
        parameters = pika.ConnectionParameters('dd.weather.gc.ca',
                                               5671,
                                               '/',
                                               credentials,
                                               ssl_options=pika.SSLOptions(context, server_hostname='weather.gc.ca'))
        return pika.BlockingConnection(parameters)

    def run(self):
        connection = None
        for attempt in range(5):
            try:
                connection = self.connect()
                channel = connection.channel()
                channel.queue_declare(queue=self.queue)
                channel.queue_bind(exchange=self.exchange, queue=self.queue, routing_key=self.routing_key)
                channel.basic_consume(queue=self.queue, on_message_callback=self.on_message, auto_ack=False)
                logging.info('starting consumer')
                channel.start_consuming()
            except Exception as e:
                logging.error(f'error: {e}')
                if connection:
                    connection.close()
                time.sleep(60)
                continue
            break
        else:
            logging.error('failed to connect after 5 attempts')
            sys.exit(1)

    def on_message(self, channel, method, properties, body):
        logging.debug(f'received message: {body}')
        topic = self.topic.lstrip('*.WXO-DD.')
        url = body.split()[1].decode() + body.split()[2].decode()
        filename = url.split('/')[-1]
        if not self.regex or self.regex.search(url):
            message = {
                'topic': topic,
                'url': url,
                'filename': filename
            }
            self.processor.process(message)
        channel.basic_ack(method.delivery_tag)

if __name__ == '__main__':
    script_path = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(script_path, 'config.json')
    config = json.load(open(config_path))
    threads = []
    for task in config['tasks']:
        consumer = ECConsumer(task)
        thread = threading.Thread(target=consumer.run)
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()