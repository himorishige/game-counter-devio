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

    # クエリーパラメータの存在確認
    if event.get("queryStringParameters"):
        username = event['queryStringParameters'].get("username")
        starttime = event['queryStringParameters'].get("starttime")
        endtime = event['queryStringParameters'].get("endtime")
    else:
        username = None

    try:
        # usernameの指定がある場合はusernameの指定した期間の一覧を出力
        if username:
            response = table.query(
                KeyConditionExpression=Key("username").eq(username) & Key(
                    "timestamp").between(int(starttime), int(endtime))
            )
        # usernameの指定がない場合は全件一覧を出力
        else:
            response = table.scan()

        if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
            raise Exception("Unable to connect to the database.")
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
