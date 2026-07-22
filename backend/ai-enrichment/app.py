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
You are an AI-powered customer support assistant.

Your job is to understand the customer's request, classify the ticket, and generate a professional draft response.

Always return ONLY valid JSON in the following format.

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
  "draftResponse": ""
}}

-------------------------
SUPPORTED ACTIONS
-------------------------

Valid actions are:

- issueRefund
- resetPassword
- getOrderStatus
- none

Only choose:

issueRefund
if the customer explicitly requests a refund.

Only choose:

resetPassword
if the customer requests password reset or cannot access their account due to forgotten credentials.

Only choose:

getOrderStatus
if the customer asks about order tracking or delivery status.

For every other request:

action = none

Examples:
- Download invoice
- Change email
- Update profile
- Subscription questions
- Billing questions
- Duplicate charges
- Login problems
- Performance issues
- Technical support
- Application errors
- General inquiries

These should all use:

action = none

-------------------------
KNOWLEDGE BASE
-------------------------

Use the Knowledge Base as the primary source of information.

Knowledge Base:
{kb_context}

Attachment Content:
{attachment_content}

Customer Subject:
{subject}

Customer Message:
{message}

-------------------------
RESPONSE RULES
-------------------------

Always generate a complete and professional draftResponse.

If the customer's issue is covered by the Knowledge Base:
- Answer using the Knowledge Base.
- Explain the solution clearly.
- Be polite and professional.
- Offer further assistance.

If no tool is required:
- Still generate a complete draftResponse.
- Never leave draftResponse empty.

If the issue requires one of the supported tools:
- Generate a draftResponse explaining what will happen.

If the customer's issue is NOT covered by the Knowledge Base:
- Politely acknowledge the request.
- Explain that additional investigation is required.
- Ask for any information needed to continue.
- Tell the customer the support team will follow up as soon as possible.

-------------------------
CATEGORY
-------------------------

Choose the most appropriate category such as:

Billing
Account
Technical
Subscription
Orders
General Inquiry

-------------------------
PRIORITY
-------------------------

Choose one:

Low
Medium
High
Critical

-------------------------
SENTIMENT
-------------------------

Choose:

Positive
Neutral
Negative

-------------------------
LANGUAGE
-------------------------

Detect the customer's language.

-------------------------
ORDER ID
-------------------------

Extract the order ID if present.

Otherwise return:

""

-------------------------
AMOUNT
-------------------------

Extract only the numeric amount if mentioned.

Examples:

"$150" -> "150"

"Refund 90.50" -> "90.50"

Otherwise return:

""

Return ONLY valid JSON.
"""

    response = bedrock.invoke_model(
        modelId="amazon.nova-lite-v1:0",
        body=json.dumps({
            "schemaVersion": "messages-v1",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "inferenceConfig": {
                "maxTokens": 700,
                "temperature": 0.2
            }
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
        "Subscription": "Support Team",
        "Orders": "Operations Team",
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
                
            else:

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
                            #st = :status
                    """,
                    ExpressionAttributeNames={
                        "#lang": "language",
                        "#st": "status"
                    },
                    ExpressionAttributeValues={
                        ":a": "COMPLETED",
                        ":c": classification.get("category", "General Inquiry"),
                        ":p": classification.get("priority", "Medium"),
                        ":sm": classification.get("sentiment", "Neutral"),
                        ":l": classification.get("language", "English"),
                        ":t": assigned_team,
                        ":tool": "None",
                        ":approval": "NOT_REQUIRED",
                        ":draft": classification.get(
                            "draftResponse",
                            "Thank you for contacting us. We have received your request and will review it shortly."
                        ),
                        ":status": "CLOSED"
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