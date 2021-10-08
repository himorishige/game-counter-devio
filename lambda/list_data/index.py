import simplejson as json
import os
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

    username = event["username"]
    starttime = event["starttime"]
    endtime = event["endtime"]

    try:
        response = table.query(
            KeyConditionExpression=Key("username").eq(username) & Key(
                "timestamp").between(starttime, endtime)
        )
        if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
            raise Exception
        else:
            status_code = 200
            res = response["Items"]
    except Exception as e:
        status_code = 500
        res = {"message": f"Internal Server Error. {str(e)}"}
    return {
        "statusCode": status_code,
        "headers": headers,
        "body": json.dumps(res)
    }
