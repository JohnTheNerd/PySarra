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
import multiprocessing
import urllib.parse
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
        self.routing_key = 'v03.post.'
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
        logging.info('shutting down consumer due to error')
        sys.exit(1)

    def on_message(self, channel, method, properties, body):
        logging.debug(f'received message: {body}')
        parsedBody = json.loads(body)
        if 'baseUrl' in parsedBody.keys() and 'relPath' in parsedBody.keys():
            topic = self.topic.lstrip('*.WXO-DD.')
            url = urllib.parse.urljoin(parsedBody['baseUrl'], parsedBody['relPath'])
            filename = url.split('/')[-1]
            message = {
                'topic': topic,
                'url': url,
                'filename': filename
            }
        if not self.regex or self.regex.search(url):
            self.processor.process(message)
        channel.basic_ack(method.delivery_tag)

if __name__ == '__main__':
    script_path = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(script_path, 'config.json')
    config = json.load(open(config_path))
    processes = []
    retries = 0
    max_retries = 5

    for task in config['tasks']:
        consumer = ECConsumer(task)
        process = multiprocessing.Process(target=consumer.run, name=json.dumps(task))
        processes.append(process)
        process.start()

    while True:
        process_restarted = False
        time.sleep(5)
        for index, process in enumerate(processes):
            if not process.is_alive():
                if retries == max_retries:
                    logging.critical(f"all restart attempts for task {process.name} failed. shutting down.")
                    for p in processes:
                        p.terminate()
                    sys.exit(1)
                logging.error(f"task {process.name} died. restarting... (attempt {retries + 1}/{max_retries})")
                consumer = ECConsumer(task)
                process = multiprocessing.Process(target=consumer.run, name=json.dumps(task))
                processes[index] = process
                process.start()
                process_restarted = True
        # do not increment the retry counter for every dead process
        if process_restarted:
            retries += 1