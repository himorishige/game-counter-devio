import simplejson as json
import os
import uuid
from datetime import datetime, timezone
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
}


def list_data(event, context):
    try:
        response = table.query(
            KeyConditionExpression=Key('username').eq('花子')
        )
        status_code = 200
        res = response['Items']
    except Exception as e:
        status_code = 500
        res = {"message": f"Internal Server Error. {str(e)}"}
    return {
        'statusCode': status_code,
        'headers': headers,
        'body': json.dumps(res)
    }
