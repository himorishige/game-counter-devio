import simplejson as json
import os
import uuid
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])

headers = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
}


def handler(event, context):
    print("Received event: " + json.dumps(event))

    uid = str(uuid.uuid4())
    username = event["username"]
    timestamp = event["timestamp"]
    flag = event["flag"]

    try:
        response = table.put_item(
            Item={
                "uid": uid,
                "username": username,
                "timestamp": timestamp,
                "flag": flag
            }
        )
        if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
            raise Exception
        else:
            status_code = 200
            res = {"message": f"Created item with id: {uid}"}
    except Exception as e:
        status_code = 500
        res = {"message": f"Internal Server Error. {str(e)}"}
    return {
        "statusCode": status_code,
        "headers": headers,
        "body": json.dumps(res)
    }
