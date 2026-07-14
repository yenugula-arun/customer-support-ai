import os
import boto3

dynamodb = boto3.resource("dynamodb")

table = dynamodb.Table(
    os.environ["TABLE_NAME"]
)

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Allow-Methods": "*"
}


def lambda_handler(event, context):

    print("EVENT:", event)

    params = event.get(
        "queryStringParameters",
        {}
    ) or {}

    ticket_id = params.get("ticketId")
    action = params.get("action")

    if not ticket_id:

        return {
            "statusCode": 400,
            "headers": {
                **CORS_HEADERS,
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "message": "Missing ticketId"
            })
        }

    if action not in ["approve", "reject"]:

        return {
            "statusCode": 400,
            "headers": {
                **CORS_HEADERS,
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "message": "Missing or invalid action"
            })
        }

    status = (
        "APPROVED"
        if action == "approve"
        else "REJECTED"
    )

    response = table.get_item(
        Key={
            "ticketId": ticket_id
        }
    )

    target_item = response.get("Item")

    if not target_item:

        return {
            "statusCode": 404,
            "headers": {
                **CORS_HEADERS,
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "message": "Ticket not found"
            })
        }

    # ---------------------------------------------------
    # Prevent multiple approvals/rejections
    # ---------------------------------------------------

    if target_item.get("approvalStatus") != "PENDING":

        return {
            "statusCode": 200,
            "headers": {
                **CORS_HEADERS,
                "Content-Type": "text/html"
            },
            "body": """
            <html>
                <head>
                    <title>Request Already Processed</title>
                </head>
                <body style="font-family:Arial;padding:40px;">
                    <h2>Request Already Processed</h2>
                    <p>
                        This approval request has already been approved or rejected.
                        No further action is required.
                    </p>
                </body>
            </html>
            """
        }

    tool_name = target_item.get(
        "toolInvoked",
        ""
    )

    if status == "APPROVED":

        if tool_name == "issueRefund":

            final_message = (
                "Your refund request has been approved and will be processed within 5-7 business days."
            )

        elif tool_name == "resetPassword":

            final_message = (
                "Your password reset request has been approved. Please check your email for further instructions."
            )

        else:

            final_message = (
                "Request approved."
            )

    else:

        if tool_name == "issueRefund":

            final_message = (
                "We reviewed your refund request, but it could not be approved based on the current refund policy."
            )

        elif tool_name == "resetPassword":

            final_message = (
                "We were unable to approve the password reset request. Please contact support for further assistance."
            )

        else:

            final_message = (
                "Request rejected."
            )

    table.update_item(
        Key={
            "ticketId": ticket_id
        },
        UpdateExpression="""
            SET
                approvalStatus = :approval,
                finalResponse = :response,
                aiStatus = :ai,
                #st = :status
        """,
        ExpressionAttributeNames={
            "#st": "status"
        },
        ExpressionAttributeValues={
            ":approval": status,
            ":response": final_message,
            ":ai": "COMPLETED",
            ":status": "CLOSED"
        }
    )

    return {
        "statusCode": 200,
        "headers": {
            **CORS_HEADERS,
            "Content-Type": "application/json"
        },
        "body": '{"message":"Success"}'
    }