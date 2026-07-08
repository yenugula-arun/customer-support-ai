import json
import boto3
import os

sns = boto3.client("sns")

dynamodb = boto3.resource("dynamodb")

table = dynamodb.Table(
    os.environ["TABLE_NAME"]
)

TOPIC_ARN = os.environ["APPROVAL_TOPIC_ARN"]
API_URL = os.environ["API_URL"]

orders = {
    "ORD-1001": "Shipped",
    "ORD-1002": "Delivered",
    "ORD-1003": "Processing"
}


def build_response(event, message):

    return {
        "messageVersion": "1.0",
        "response": {
            "actionGroup": event["actionGroup"],
            "function": event["function"],
            "functionResponse": {
                "responseBody": {
                    "TEXT": {
                        "body": message
                    }
                }
            }
        }
    }


def get_parameter(event, parameter_name):

    for parameter in event.get("parameters", []):

        if parameter["name"] == parameter_name:
            return parameter["value"]

    return None

def get_order_status(event):

    ticket_id = get_parameter(
        event,
        "ticketId"
    )

    order_id = get_parameter(
        event,
        "orderId"
    )

    if not order_id:

        return build_response(
            event,
            "Order ID not provided."
        )

    status = orders.get(
        order_id,
        "Order not found"
    )

    final_response = (
        f"Your order {order_id} is currently '{status}'."
    )

    if ticket_id:

        table.update_item(
            Key={
                "ticketId": ticket_id
            },
            UpdateExpression="""
                SET
                    finalResponse = :f,
                    approvalStatus = :a,
                    aiStatus = :ai,
                    #st = :s
            """,
            ExpressionAttributeNames={
                "#st": "status"
            },
            ExpressionAttributeValues={
                ":f": final_response,
                ":a": "NOT_REQUIRED",
                ":ai": "COMPLETED",
                ":s": "CLOSED"
            }
        )

    return build_response(
        event,
        final_response
    )

def reset_password(event):

    ticket_id = get_parameter(
        event,
        "ticketId"
    )

    customer_id = get_parameter(
        event,
        "customerId"
    )

    approve_link = (
        f"{API_URL}/approve"
        f"?ticketId={ticket_id}"
        f"&action=approve"
    )

    reject_link = (
        f"{API_URL}/reject"
        f"?ticketId={ticket_id}"
        f"&action=reject"
    )
    print("Publishing Password Reset SNS message...")
    print(f"Topic ARN: {TOPIC_ARN}")

    response = sns.publish(
        TopicArn=TOPIC_ARN,
        Subject="Password Reset Approval Required",
        Message=(
            f"Customer ID: {customer_id}\n"
            f"Request Type: PASSWORD_RESET\n\n"
            f"Approve:\n{approve_link}\n\n"
            f"Reject:\n{reject_link}"
        )
    )

    print("SNS RESPONSE")
    print(response)

    return build_response(
        event,
        f"Password reset request submitted for customer {customer_id}."
    )


def issue_refund(event):

    ticket_id = get_parameter(
        event,
        "ticketId"
    )

    order_id = get_parameter(
        event,
        "orderId"
    )

    amount = get_parameter(
        event,
        "amount"
    )

    approve_link = (
        f"{API_URL}/approve"
        f"?ticketId={ticket_id}"
        f"&action=approve"
    )

    reject_link = (
        f"{API_URL}/reject"
        f"?ticketId={ticket_id}"
        f"&action=reject"
    )

    print("Publishing Refund SNS message...")
    print(f"Topic ARN: {TOPIC_ARN}")

    response = sns.publish(
        TopicArn=TOPIC_ARN,
        Subject="Refund Approval Required",
        Message=(
            f"Order ID: {order_id}\n"
            f"Request Type: REFUND\n"
            f"Amount: {amount}\n\n"
            f"Approve:\n{approve_link}\n\n"
            f"Reject:\n{reject_link}"
        )
    )

    print("SNS RESPONSE")
    print(response)

    return build_response(
        event,
        f"Refund request submitted for order {order_id} and amount {amount}."
    )


def lambda_handler(event, context):

    print("EVENT RECEIVED")
    print(json.dumps(event))

    try:

        function_name = event["function"]

        if function_name == "getOrderStatus":

            return get_order_status(
                event
            )

        elif function_name == "resetPassword":

            return reset_password(
                event
            )

        elif function_name == "issueRefund":

            return issue_refund(
                event
            )

        return build_response(
            event,
            "Unknown function."
        )

    except Exception as e:

        print("ERROR")
        print(str(e))

        return build_response(
            event,
            str(e)
        )