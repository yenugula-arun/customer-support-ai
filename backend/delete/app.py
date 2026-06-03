import json
import boto3
import os

dynamodb = boto3.resource("dynamodb")

table = dynamodb.Table(os.environ["TABLE_NAME"])


def lambda_handler(event, context):

    try:

        ticket_id = event["pathParameters"]["ticketId"]

        table.delete_item(
            Key={
                "ticketId": ticket_id
            }
        )

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Ticket deleted successfully"
            })
        }

    except Exception as e:

        print("ERROR:", str(e))

        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": str(e)
            })
        }