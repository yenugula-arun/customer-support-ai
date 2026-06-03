import json
import boto3
import os
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")

table = dynamodb.Table(os.environ["TABLE_NAME"])


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


def lambda_handler(event, context):

    path_parameters = event.get("pathParameters")

    # GET SINGLE TICKET
    if path_parameters and path_parameters.get("ticketId"):

        ticket_id = path_parameters["ticketId"]

        response = table.get_item(
            Key={
                "ticketId": ticket_id
            }
        )

        item = response.get("Item")

        if not item:
            return {
                "statusCode": 404,
                "body": json.dumps({
                    "message": "Ticket not found"
                })
            }

        return {
            "statusCode": 200,
            "body": json.dumps(item, cls=DecimalEncoder)
        }

    # GET ALL TICKETS
    response = table.scan()

    items = response.get("Items", [])

    return {
        "statusCode": 200,
        "body": json.dumps(items, cls=DecimalEncoder)
    }