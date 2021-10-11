import simplejson as json
import os
import uuid
import datetime
import boto3
from boto3.dynamodb.conditions import Key
import requests

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])

headers = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
}

# SSMパラメーターストアから値を取得


def get_parameters(param_key):
    ssm = boto3.client('ssm')
    response = ssm.get_parameter(
        Name=param_key,
        WithDecryption=True
    )
    return response['Parameter']['Value']


# UNIX時間をJSTのdatetimeに変換


def convert_timestamp(target):
    result = datetime.datetime.fromtimestamp(
        target, datetime.timezone(datetime.timedelta(hours=9)))
    return result


def handler(event, context):
    print("Received event: " + json.dumps(event))

    # クエリーパラメータの存在確認
    if event.get("body"):
        parsed = json.loads(event["body"])
        uid = str(uuid.uuid4())
        username = parsed["username"]
        timestamp = parsed["timestamp"]
        date = convert_timestamp(parsed["timestamp"]).date().isoformat()
        time = convert_timestamp(parsed["timestamp"]).time().isoformat()
        flag = parsed["flag"]
    else:
        username = None

    try:
        # usernameがある場合はDynamoDBにデータを登録
        if username:
            response = table.put_item(
                Item={
                    "uid": uid,
                    "username": username,
                    "timestamp": int(timestamp),
                    "date": date,
                    "time": time,
                    "flag": flag
                }
            )
            if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
                raise Exception("Unable to connect to the database.")
            else:
                status_code = 200
                res = {"message": f"Created item with id: {uid}"}

            # LINEへ通知
            line_token = get_parameters("/GameCounter/LineToken")
            line_url = "https://notify-api.line.me/api/notify"
            line_headers = {"Authorization": "Bearer " + line_token}
            line_message = "flag未取得"

            if flag == "start":
                line_message = username + "がゲームを開始しました"
            if flag == "end":
                line_message = username + "がゲームを終了しました"

            payload = {"message": line_message}

            requests.post(
                line_url, headers=line_headers,
                params=payload
            )

        # usernameがない場合はエラーとして終了
        else:
            raise Exception("Parameter is missing.")

    except Exception as e:
        status_code = 500
        res = {"message": f"Internal Server Error. {str(e)}"}
    return {
        "statusCode": status_code,
        "headers": headers,
        "body": json.dumps(res)
    }
