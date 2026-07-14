import json
import boto3
import os

sqs = boto3.client("sqs")

QUEUE_URL = os.environ["QUEUE_URL"]

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Allow-Methods": "*"
}


def lambda_handler(event, context):

    body = json.loads(event["body"])

    customer_email = event["requestContext"]["authorizer"]["claims"]["email"]

    body["customerEmail"] = customer_email

    sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=json.dumps(body)
    )

    return {
        "statusCode": 200,
        "headers": CORS_HEADERS,
        "body": json.dumps({
            "message": "Ticket queued successfully"
        })
    }