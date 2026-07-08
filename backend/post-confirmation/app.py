import boto3

cognito = boto3.client("cognito-idp")


def lambda_handler(event, context):

    user_pool_id = event["userPoolId"]

    username = event["userName"]

    print(f"Adding {username} to Customer group")

    cognito.admin_add_user_to_group(
        UserPoolId=user_pool_id,
        Username=username,
        GroupName="Customer"
    )

    print("Successfully added user to Customer group")

    return event