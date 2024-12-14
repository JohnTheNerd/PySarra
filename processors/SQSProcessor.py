import boto3
import json

sqs = boto3.client('sqs')
queue_url = 'https://sqs.<region>.amazonaws.com/<account-id>/<queue-name>'

def process(message):
    try:
        response = sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(message)
        )
        print(f'message sent to sqs: {response["MessageId"]}')
    except Exception as e:
        print(f'error sending message to sqs: {e}')