from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_dynamodb as dynamodb,
    aws_lambda as lambda_,
    aws_apigateway as apigw
)
from constructs import Construct
import os


class GameCounterStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # DynamoDB ログデータ格納用
        table = dynamodb.Table(self, "GameCounterTable",
                               table_name="GameCounter",
                               partition_key=dynamodb.Attribute(
                                   name="username", type=dynamodb.AttributeType.STRING),
                               sort_key=dynamodb.Attribute(
                                   name="timestamp", type=dynamodb.AttributeType.NUMBER),
                               billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
                               removal_policy=RemovalPolicy.DESTROY
                               )

        # Lambda ログデータ一覧表示用
        list_data = lambda_.Function(self, "ListData", code=lambda_.Code.from_asset(
            "lambda"), handler="counter.list_data", runtime=lambda_.Runtime.PYTHON_3_9,
            environment={'TABLE_NAME': table.table_name})

        table.grant_read_data(list_data)
