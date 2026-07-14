import json
import boto3
import os
import base64
import uuid

s3 = boto3.client("s3")

BUCKET_NAME = os.environ["BUCKET_NAME"]

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Allow-Methods": "*"
}

def lambda_handler(event, context):

    try:

        body = json.loads(event["body"])

        file_name = body["fileName"]

        file_content = body["fileContent"]

        decoded_file = base64.b64decode(file_content)

        unique_file_name = f"{uuid.uuid4()}-{file_name}"

        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=unique_file_name,
            Body=decoded_file
        )

        file_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{unique_file_name}"

        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "message": "File uploaded successfully",
                "fileKey": unique_file_name,
                "fileUrl": file_url
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