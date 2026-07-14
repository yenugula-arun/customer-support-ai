import json
import boto3
import os

dynamodb = boto3.resource("dynamodb")

table = dynamodb.Table(
    os.environ["TABLE_NAME"]
)

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Allow-Methods": "*"
}

VALID_STATUSES = [
    "OPEN",
    "IN_PROGRESS",
    "RESOLVED",
    "CLOSED"
]


def lambda_handler(event, context):

    try:

        ticket_id = event["pathParameters"]["ticketId"]

        body = json.loads(event["body"])

        update_expression = []
        expression_values = {}
        expression_names = {}

        if "status" in body:

            if body["status"] not in VALID_STATUSES:
                return {
                    "statusCode": 400,
                    "headers": CORS_HEADERS,
                    "body": json.dumps({
                        "message": "Invalid status"
                    })
                }

            update_expression.append("#st = :status")

            expression_values[":status"] = body["status"]

            expression_names["#st"] = "status"

        if "assignedTo" in body:

            update_expression.append(
                "assignedTo = :assignedTo"
            )

            expression_values[":assignedTo"] = (
                body["assignedTo"]
            )

        if not update_expression:

            return {
                "statusCode": 400,
                "headers": CORS_HEADERS,
                "body": json.dumps({
                    "message": "No fields provided for update"
                })
            }

        table.update_item(
            Key={
                "ticketId": ticket_id
            },
            UpdateExpression="SET " + ", ".join(update_expression),
            ExpressionAttributeValues=expression_values,
            ExpressionAttributeNames=expression_names
        )

        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "message": "Ticket updated successfully"
            })
        }

    except Exception as e:

        print("ERROR:", str(e))

        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "message": str(e)
            })
        }