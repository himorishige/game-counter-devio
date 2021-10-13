import simplejson as json
import os
import boto3
from boto3.dynamodb.conditions import Key, Attr
import datetime

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])
log_table = dynamodb.Table(os.environ["LOG_TABLE_NAME"])


def query_today(username, target_date):
    response = table.query(
        KeyConditionExpression=Key("username").eq(username),
        FilterExpression=Attr("date").eq(target_date)
    )
    return response["Items"]


def create_total_time(log_data):
    total = 0

    for i, item in enumerate(log_data):
        temp = 0

        try:
            if log_data[i + 1].get("flag") == 'end':
                temp = int(log_data[i + 1]["timestamp"]) - \
                    int(item["timestamp"])
        except:
            print('done')

        total += temp

    return total


def handler(event, context):

    # 24時過ぎの計測を想定するため1日前の日付に変換
    today = str((datetime.datetime.now(
        datetime.timezone(datetime.timedelta(hours=9))) - datetime.timedelta(days=1)).date())

    try:

        # 対象の今日のログを集計、DBへ格納する
        targets = ["Lucy", "Mike"]

        for target in targets:
            res = query_today(target, today)
            total_time = create_total_time(res)
            data = str(datetime.timedelta(seconds=total_time or 0))

            if data:
                response = log_table.put_item(
                    Item={
                        "username": target,
                        "date": today,
                        "totaltime": data,
                    }
                )

    except Exception as e:
        print(f"Internal Server Error. {str(e)}")

    return "OK"
