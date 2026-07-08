import json
import boto3
import os
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")

table = dynamodb.Table(
    os.environ["TABLE_NAME"]
)


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


def lambda_handler(event, context):

    print(json.dumps(event))

    claims = event["requestContext"]["authorizer"]["claims"]

    user_email = claims["email"]

    user_group = claims.get(
        "cognito:groups",
        ""
    )

    path_parameters = event.get(
        "pathParameters"
    )

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

        # CUSTOMER CAN ONLY VIEW OWN TICKET
        if (
            user_group == "Customer"
            and item.get("customerEmail") != user_email
        ):
            return {
                "statusCode": 403,
                "body": json.dumps({
                    "message": "Access denied"
                })
            }

        return {
            "statusCode": 200,
            "body": json.dumps(
                item,
                cls=DecimalEncoder
            )
        }

    # GET ALL TICKETS

    response = table.scan()

    items = response.get(
        "Items",
        []
    )

    # CUSTOMER -> ONLY OWN TICKETS
    if user_group == "Customer":

        items = [
            item
            for item in items
            if item.get("customerEmail") == user_email
        ]

    return {
        "statusCode": 200,
        "body": json.dumps(
            items,
            cls=DecimalEncoder
        )
    }