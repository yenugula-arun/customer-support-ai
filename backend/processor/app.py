import json
import boto3
import uuid
import os
from datetime import datetime

dynamodb = boto3.resource("dynamodb")

table = dynamodb.Table(
    os.environ["TABLE_NAME"]
)


def lambda_handler(event, context):

    for record in event["Records"]:

        body = json.loads(
            record["body"]
        )

        ticket = {
            "ticketId": f"TKT-{uuid.uuid4()}",

            "customerEmail": body.get(
                "customerEmail"
            ),

            "orderId": body.get(
                "orderId"
            ),

            "amount": body.get(
                "amount"
            ),

            "subject": body.get(
                "subject"
            ),

            "message": body.get(
                "message"
            ),

            "attachmentKey": body.get(
                "attachmentKey"
            ),

            "status": "OPEN",

            "aiStatus": "PENDING",

            "assignedTo": "",

            "source": "API",

            "createdAt": datetime.utcnow().isoformat()
        }

        table.put_item(
            Item=ticket
        )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message":
            "Tickets processed successfully"
        })
    }