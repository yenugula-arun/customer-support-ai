import json
import boto3
import os

sqs = boto3.client("sqs")

QUEUE_URL = os.environ["QUEUE_URL"]

def lambda_handler(event, context):

    body = json.loads(event["body"])

    ticket = {
        "customerId": body.get("customerId"),
        "subject": body.get("subject"),
        "message": body.get("message"),
        "attachmentKey": body.get("attachmentKey")
    }

    sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=json.dumps(ticket)
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Ticket queued successfully"
        })
    }