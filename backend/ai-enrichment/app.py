import json
import boto3
import os

lambda_client = boto3.client(
    "lambda",
    region_name="us-east-1"
)

SUPPORT_TOOLS_FUNCTION_NAME = os.environ[
    "SUPPORT_TOOLS_FUNCTION_NAME"
]

s3 = boto3.client("s3")

dynamodb = boto3.resource("dynamodb")

bedrock = boto3.client(
    "bedrock-runtime",
    region_name="us-east-1"
)

bedrock_agent = boto3.client(
    "bedrock-agent-runtime",
    region_name="us-east-1"
)

table = dynamodb.Table(
    os.environ["TABLE_NAME"]
)

KB_ID = os.environ["KNOWLEDGE_BASE_ID"]


def retrieve_context(query):

    response = bedrock_agent.retrieve(
        knowledgeBaseId=KB_ID,
        retrievalQuery={
            "text": query
        }
    )

    if not response["retrievalResults"]:
        return "Information not available in knowledge base."

    contexts = []

    for result in response["retrievalResults"]:

        contexts.append(
            result["content"]["text"]
        )

    return "\n".join(
        contexts[:3]
    )


def get_attachment_content(
    attachment_key
):

    if not attachment_key:
        return ""

    try:

        response = s3.get_object(
            Bucket=os.environ["BUCKET_NAME"],
            Key=attachment_key
        )

        content = (
            response["Body"]
            .read()
            .decode("utf-8")
        )

        return content

    except Exception as e:

        print(
            f"Attachment read error: {str(e)}"
        )

        return ""


def classify_ticket(
    subject,
    message,
    attachment_content,
    kb_context
):

    prompt = f"""
You are a customer support AI.

Return ONLY valid JSON.

{{
  "category": "",
  "priority": "",
  "sentiment": "",
  "language": "",
  "suggestedResolution": "",
  "action": "",
  "orderId": "",
  "customerId": "",
  "amount": "",
  "draftResponse": "Professional AI response"
}}

Actions:
- none
- issueRefund
- resetPassword
- getOrderStatus

If customer requests a refund:
action = issueRefund

If customer requests password reset:
action = resetPassword

If customer asks order status:
action = getOrderStatus

Extract orderId from the message if present.

If an amount is mentioned in the message,
extract only the numeric value.

Examples:

"Refund 90.99 dollars"
amount = "90.99"

"Refund $150"
amount = "150"

"Amount paid was 299"
amount = "299"

If no amount exists:
amount = ""

Knowledge Base Context:
{kb_context}

Attachment Content:
{attachment_content}

Subject:
{subject}

Message:
{message}
"""

    response = bedrock.invoke_model(
        modelId="amazon.nova-lite-v1:0",
        body=json.dumps({
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        })
    )

    response_body = json.loads(
        response["body"].read()
    )

    result_text = (
        response_body["output"]
        ["message"]
        ["content"][0]
        ["text"]
    )

    result_text = (
        result_text
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    return json.loads(
        result_text
    )


def get_assigned_team(
    department
):

    team_mapping = {
        "Billing": "Finance Team",
        "Technical": "Engineering Team",
        "Account": "Support Team",
        "General Inquiry": "Customer Care Team"
    }

    return team_mapping.get(
        department,
        "Support Team"
    )


def lambda_handler(
    event,
    context
):

    for record in event["Records"]:

        if record["eventName"] != "INSERT":
            continue

        new_image = (
            record["dynamodb"]
            .get("NewImage", {})
        )

        if "subject" not in new_image:
            continue

        if "message" not in new_image:
            continue

        if "aiStatus" not in new_image:
            continue

        if (
            new_image["aiStatus"]["S"]
            != "PENDING"
        ):
            continue

        ticket_id = (
            new_image["ticketId"]["S"]
        )

        subject = (
            new_image["subject"]["S"]
        )

        message = (
            new_image["message"]["S"]
        )

        attachment_key = None

        if (
            "attachmentKey" in new_image
            and "S" in new_image["attachmentKey"]
        ):

            attachment_key = (
                new_image["attachmentKey"]["S"]
            )

        try:

            attachment_content = (
                get_attachment_content(
                    attachment_key
                )
            )

            kb_context = (
                retrieve_context(
                    f"{subject} {message}"
                )
            )

            classification = (
                classify_ticket(
                    subject,
                    message,
                    attachment_content,
                    kb_context
                )
            )

            action = classification.get(
                "action",
                "none"
            )

            assigned_team = (
                get_assigned_team(
                    classification["category"]
                )
            )

            if action == "issueRefund":

                payload = {
                    "actionGroup": "SupportTools",
                    "function": "issueRefund",
                    "parameters": [
                        {
                            "name": "ticketId",
                            "value": ticket_id
                        },
                        {
                            "name": "orderId",
                            "value": classification.get(
                                "orderId",
                                ""
                            )
                        },
                        {
                            "name": "amount",
                            "value": classification.get(
                                "amount",
                                ""
                             )
                        }
                    ]
                }

                lambda_client.invoke(
                    FunctionName=SUPPORT_TOOLS_FUNCTION_NAME,
                    InvocationType="RequestResponse",
                    Payload=json.dumps(payload)
                )

                table.update_item(
                    Key={
                        "ticketId": ticket_id
                    },
                    UpdateExpression="""
                        SET
                            aiStatus = :a,
                            category = :c,
                            priority = :p,
                            sentiment = :sm,
                            #lang = :l,
                            assignedTo = :t,
                            toolInvoked = :tool,
                            approvalStatus = :approval,
                            draftResponse = :draft,
                            #st = :status,
                            orderId = :oid,
                            amount = :amt
                    """,
                    ExpressionAttributeNames={
                        "#lang": "language",
                        "#st": "status"
                    },
                    ExpressionAttributeValues={
                        ":a": "COMPLETED",
                        ":c": classification["category"],
                        ":p": classification["priority"],
                        ":sm": classification.get(
                            "sentiment",
                            "Neutral"
                        ),
                        ":l": classification.get(
                            "language",
                            "English"
                        ),
                        ":t": assigned_team,
                        ":tool": "issueRefund",
                        ":approval": "PENDING",
                        ":status": "PENDING",
                        ":oid": classification.get(
                            "orderId",
                            ""
                        ),
                        ":amt": classification.get(
                            "amount",
                            ""
                        ),
                        ":draft": classification.get(
                            "draftResponse",
                            ""
                        ),
                    }
                )

            elif action == "resetPassword":

                payload = {
                    "actionGroup": "SupportTools",
                    "function": "resetPassword",
                    "parameters": [
                        {
                            "name": "ticketId",
                            "value": ticket_id
                        },
                        {
                            "name": "customerEmail",
                            "value": new_image.get(
                                "customerEmail",
                                {}
                            ).get(
                                "S",
                                ""
                            )
                        }
                    ]
                }

                lambda_client.invoke(
                    FunctionName=SUPPORT_TOOLS_FUNCTION_NAME,
                    InvocationType="RequestResponse",
                    Payload=json.dumps(payload)
                )

                table.update_item(
                    Key={
                        "ticketId": ticket_id
                    },
                    UpdateExpression="""
                        SET
                            aiStatus = :a,
                            category = :c,
                            priority = :p,
                            sentiment = :sm,
                            #lang = :l,
                            assignedTo = :t,
                            toolInvoked = :tool,
                            approvalStatus = :approval,
                            draftResponse = :draft,
                            #st = :status,
                            customerEmail = :email
                    """,
                    ExpressionAttributeNames={
                        "#lang": "language",
                        "#st": "status"
                    },
                    ExpressionAttributeValues={
                        ":a": "COMPLETED",
                        ":c": classification["category"],
                        ":p": classification["priority"],
                        ":sm": classification.get(
                            "sentiment",
                            "Neutral"
                        ),
                        ":l": classification.get(
                            "language",
                            "English"
                        ),
                        ":t": assigned_team,
                        ":tool": "resetPassword",
                        ":approval": "PENDING",
                        ":draft": classification.get(
                            "draftResponse",
                            ""
                        ),
                        ":status": "PENDING",
                        ":email": new_image.get(
                            "customerEmail",
                            {}
                        ).get(
                            "S",
                            ""
                        )
                    }
                )

            elif action == "getOrderStatus":

                payload = {
                    "actionGroup": "SupportTools",
                    "function": "getOrderStatus",
                    "parameters": [
                        {
                            "name": "orderId",
                            "value": classification.get(
                                "orderId",
                                ""
                            )
                        }
                    ]
                }

                response = lambda_client.invoke(
                    FunctionName=SUPPORT_TOOLS_FUNCTION_NAME,
                    InvocationType="RequestResponse",
                    Payload=json.dumps(payload)
                )

                tool_response = json.loads(
                    response["Payload"].read()
                )

                final_response = (
                    tool_response["response"]
                    ["functionResponse"]
                    ["responseBody"]
                    ["TEXT"]
                    ["body"]
                )

                table.update_item(
                    Key={
                        "ticketId": ticket_id
                    },
                    UpdateExpression="""
                        SET
                            aiStatus = :a,
                            category = :c,
                            priority = :p,
                            sentiment = :sm,
                            #lang = :l,
                            assignedTo = :t,
                            toolInvoked = :tool,
                            approvalStatus = :approval,
                            draftResponse = :draft,
                            finalResponse = :draft,
                            #st = :status,
                            orderId = :oid
                    """,
                    ExpressionAttributeNames={
                        "#lang": "language",
                        "#st": "status"
                    },
                    ExpressionAttributeValues={
                        ":a": "COMPLETED",
                        ":c": classification["category"],
                        ":p": classification["priority"],
                        ":sm": classification.get(
                            "sentiment",
                            "Neutral"
                        ),
                        ":l": classification.get(
                            "language",
                            "English"
                        ),
                        ":t": assigned_team,
                        ":tool": "getOrderStatus",
                        ":approval": "NOT_REQUIRED",
                        ":draft": final_response,
                        ":status": "CLOSED",
                        ":oid": classification.get(
                            "orderId",
                            ""
                        )
                    }
                )

        except Exception as e:

            print(
                f"AI enrichment error: {str(e)}"
            )

            table.update_item(
                Key={
                    "ticketId": ticket_id
                },
                UpdateExpression="""
                    SET aiStatus = :a
                """,
                ExpressionAttributeValues={
                    ":a": "FAILED"
                }
            )

            raise

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "AI enrichment completed"
            }
        )
    }