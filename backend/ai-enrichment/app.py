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

Before generating the JSON:

1. Identify the customer's primary intent.
2. Decide whether the intent exactly matches one of the supported actions.
3. If it does not exactly match a supported action, choose:
   action = none
4. Use the Knowledge Base to answer whenever possible.
5. Generate the draftResponse based on the Knowledge Base.
6. Finally produce the JSON.

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

---------------------
SUPPORTED ACTIONS
---------------------
Choose exactly one action.

Decision order:

1. Choose issueRefund ONLY when the customer's primary intent is to receive a refund.

Examples:

- "I want a refund."
- "Please refund my payment."
- "Refund my money."
- "I was charged twice. Please refund the extra charge."
- "My order was cancelled. I want my money back."
- "I received a defective product and want a refund."

→ action = issueRefund

Do NOT use issueRefund when the customer is only:

- Asking about billing
- Reporting a duplicate charge without requesting a refund
- Asking why they were charged
- Requesting an explanation
- Requesting invoice information

These requests must use:

action = none

2. Does the customer explicitly ask to reset their password or cannot access the account due to forgotten credentials?
→ resetPassword

3. Does the customer explicitly ask:
- Where is my order?
- Track my order
- Shipment status
- Delivery status
- Has my order shipped?
- When will my order arrive?

→ getOrderStatus

4. Otherwise

→ none

Never infer an action.
Never guess an action.
Never choose the closest action.

Only use an action when there is an exact match.

-------------------------
KNOWLEDGE BASE
-------------------------

Use the Knowledge Base as the primary source of truth.

If the customer's question is answered by the Knowledge Base, answer using only that information.

Do not invent policies, procedures, pricing, refund rules, or troubleshooting steps that are not present in the Knowledge Base.

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

The draftResponse should contain ONLY the response body.

Do NOT include:
- Greetings (Dear Customer, Hello, Hi, etc.)
- Customer name
- Signatures
- Closing signatures such as "Best regards", "Regards", "Sincerely"
- Team names such as "Customer Support Team"
- Placeholders like [Customer Name], [Your Name], [Company Name]

Begin directly with the solution or explanation.

If the customer's issue is covered by the Knowledge Base:
- Answer using the Knowledge Base.
- Explain the solution clearly.
- Be polite and professional.
- End with a short offer for additional assistance.

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

Choose exactly one category from:

- Billing
- Account
- Technical
- Subscription
- Orders
- General Inquiry

Do not create new categories.

-------------------------
PRIORITY
-------------------------

Choose exactly one priority.

Critical
- Security incidents
- Complete service outage
- Data loss

High
- Customer cannot access their account
- Payment failures
- Explicit refund requests

Medium
- Billing questions
- Order questions
- Technical issues
- Subscription requests

Low
- General inquiries
- Information requests
- Documentation requests

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

Do not include markdown.

Do not include explanations.

Do not include text before or after the JSON.

Every field in the schema must always be present.

If a value is unavailable, return an empty string ("").

Every JSON value must be a string.
Do not return null, arrays, or objects.

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