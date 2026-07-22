import os
import boto3
import json

dynamodb = boto3.resource("dynamodb")

bedrock = boto3.client(
    "bedrock-runtime",
    region_name="us-east-1"
)

bedrock_agent = boto3.client(
    "bedrock-agent-runtime",
    region_name="us-east-1"
)


KB_ID = os.environ["KNOWLEDGE_BASE_ID"]


table = dynamodb.Table(
    os.environ["TABLE_NAME"]
)

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Allow-Methods": "*"
}



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


def generate_final_response(
    subject,
    message,
    draft_response,
    approval_status,
    tool_name,
    kb_context
):

    prompt = f"""
You are an experienced customer support specialist writing the final response that will be sent directly to the customer.

Knowledge Base:
{kb_context}

Customer Subject:
{subject}

Customer Message:
{message}

Current Draft Response:
{draft_response}

Approval Status:
{approval_status}

Rules:

- Use the Current Draft Response as the primary source.
- Preserve the meaning of the draft response.
- Improve grammar, clarity, professionalism and empathy.
- Never include a subject line.
- Never include greetings such as "Dear Customer".
- Never include signatures.
- Never use placeholders.
- Return only the response text.

If Approval Status is APPROVED:
- Clearly tell the customer that their request has been approved or successfully processed.
- Use the draft response to explain the resolution.
- End with a friendly offer for additional assistance.

If Approval Status is REJECTED:
- Start with an empathetic acknowledgement of the customer's issue.
- Clearly explain that, after reviewing the request, it could not be approved or completed.
- Use the draft response and Knowledge Base to provide the best available alternative or next steps.
- End with a supportive offer for further assistance.

Return ONLY the final response.
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
                "maxTokens": 350,
                "temperature": 0.2
            }
        })
    )

    response_body = json.loads(
        response["body"].read()
    )

    final_response = (
        response_body["output"]
        ["message"]
        ["content"][0]
        ["text"]
    )

    return final_response.strip()


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

    draft_response = target_item.get(
        "draftResponse",
        ""
    )

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

    subject = target_item.get("subject", "")
    message = target_item.get("message", "")


    final_message = draft_response

    try:
        kb_context = retrieve_context(
            f"{subject} {message}"
        )

        final_message = generate_final_response(
            subject=subject,
            message=message,
            draft_response=draft_response,
            approval_status=status,
            tool_name=tool_name,
            kb_context=kb_context
        )
    
        if status == "APPROVED":
            final_message = (
                "Your request has been successfully approved.\n\n"
                + final_message
            )
        else:
            final_message = (
                "We understand your concern. After carefully reviewing your request, "
                "we're unable to complete the requested action at this time.\n\n"
                + final_message
            )

    except Exception as e:
        print(f"Final response generation failed: {e}")


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