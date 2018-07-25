from google.cloud import pubsub
import json
publisher = pubsub.PublisherClient()
projectName = "your-project-name"

def process(message):
  topic = 'projects/' + projectName + '/topics/' + message['topic']
  publisher.publish(topic, json.dumps(str(message)).encode('utf-8'))
