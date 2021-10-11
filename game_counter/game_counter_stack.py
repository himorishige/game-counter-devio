from aws_cdk import (
    Stack,
    RemovalPolicy,
    Duration,
    CfnOutput,
    aws_dynamodb as dynamodb,
    aws_lambda as lambda_,
    aws_iam as iam,
    aws_apigateway as apigateway,
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
    aws_events as events,
    aws_events_targets as targets
)
from constructs import Construct


class GameCounterStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # DynamoDB ログデータ格納用
        table = dynamodb.Table(
            self, "GameCounterTable",
            table_name="GameCounter",
            partition_key=dynamodb.Attribute(
                name="username", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(
                name="timestamp", type=dynamodb.AttributeType.NUMBER),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        # DynamoDB 統計データ格納用
        log_table = dynamodb.Table(
            self, "GameCounterLogTable",
            table_name="GameCounterLog",
            partition_key=dynamodb.Attribute(
                name="username", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(
                name="date", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        # Lambda用共通パラメーター
        common_params = {
            "runtime": lambda_.Runtime.PYTHON_3_9,
            "timeout": Duration.seconds(10),
        }

        # Lambda データ一覧表示用
        list_data = lambda_.Function(
            self, "ListData",
            code=lambda_.Code.from_asset("lambda/list_data"),
            handler="index.handler",
            function_name="GameCounter-ListData",
            environment={
                "TABLE_NAME": table.table_name,
            },
            **common_params
        )

        # DynamoDBへ権限を付与
        table.grant_read_data(list_data)

        # SSMへのアクセス用のIAMロールを設定
        role_for_lambda = iam.Role(
            self, "Role",
            role_name="GameCounterSSMRole",
            assumed_by=iam.ServicePrincipal(
                "lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    'service-role/AWSLambdaBasicExecutionRole'),
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    'AmazonSSMReadOnlyAccess')
            ]
        )

        # Lambda データ投稿用
        push_data = lambda_.Function(
            self, "PushData",
            code=lambda_.Code.from_asset("lambda/push_data"),
            handler="index.handler",
            function_name="GameCounter-PushData",
            # LINEトークンをSSMから取得するためにRoleを割り当て
            role=role_for_lambda,
            environment={
                "TABLE_NAME": table.table_name,
            },
            **common_params
        )

        # DynamoDBへ権限を付与
        table.grant_write_data(push_data)

        # Lambda ログデータ統計用
        create_log = lambda_.Function(
            self, "CreateLog",
            code=lambda_.Code.from_asset("lambda/create_log"),
            handler="index.handler",
            function_name="GameCounter-CreateLog",
            environment={
                "TABLE_NAME": table.table_name,
                "LOG_TABLE_NAME": log_table.table_name,
            },
            **common_params
        )

        # DynamoDBへ権限を付与
        table.grant_read_data(create_log)
        log_table.grant_write_data(create_log)

        # Lambda データ一覧表示用
        list_log = lambda_.Function(
            self, "ListLog",
            code=lambda_.Code.from_asset("lambda/list_log"),
            handler="index.handler",
            function_name="GameCounter-ListLog",
            environment={
                "LOG_TABLE_NAME": log_table.table_name,
            },
            **common_params
        )

        # DynamoDBへ権限を付与
        log_table.grant_read_data(list_log)

        # ApiGatewayを作成
        api = apigateway.RestApi(
            self, "GameCounterApi",
            default_cors_preflight_options={
                "allow_origins": apigateway.Cors.ALL_ORIGINS,
                "allow_methods": apigateway.Cors.ALL_METHODS
            })

        # ApiGatewayのURI/counterというエンドポイントを作成
        counter_list = api.root.add_resource("counter")

        # /counter にGETでアクセスの際には一覧表示のLambdaを割り当てる
        counter_list.add_method(
            "GET", apigateway.LambdaIntegration(list_data),
            api_key_required=True
        )

        # /counter にPOSTでアクセスの際にはログ書き込みのLambdaを割り当てる
        counter_list.add_method(
            "POST", apigateway.LambdaIntegration(push_data),
            api_key_required=True
        )

        # 統計データ取得用のエンドポイント作成（counter/log）
        log_list = counter_list.add_resource("log")

        # /counter/log にGETでアクセスの際にはログ一覧表示のLambdaを割り当てる
        log_list.add_method(
            "GET", apigateway.LambdaIntegration(list_log),
            api_key_required=True
        )

        # API Keyを利用するために利用料プランとAPI KEYを作成
        plan = api.add_usage_plan(
            "UsagePlan",
            name="GameCounterPlan",
            throttle={
                "rate_limit": 10,
                "burst_limit": 2
            },
            api_stages=[{"api": api, "stage": api.deployment_stage}]
        )

        key = api.add_api_key(
            "GameCounterApiKey",
            api_key_name="GameCounterApiKey"
        )
        plan.add_api_key(key)

        # API Keyを確認するためにAPI KeyのIDをコンソールに出力
        CfnOutput(
            self, "GameCounterApiKeyExport",
                  value=key.key_id,
                  export_name="GameCounterApiKeyId"
        )

        # S3 Bucket フロントエンド公開用
        bucket = s3.Bucket(
            self, "GameCounterBucket",
            website_index_document="index.html",
            public_read_access=True,
            removal_policy=RemovalPolicy.DESTROY
        )

        # S3 BucketにReactからビルドしたファイルをアップロード
        s3deploy.BucketDeployment(
            self, "GameCounterBucketDeployment",
            destination_bucket=bucket,
            sources=[s3deploy.Source.asset("frontend/build")],
            retain_on_delete=False
        )

        # S3 Bucketの公開URLを出力
        CfnOutput(
            self, "GameCounterS3PublickUrl",
                  value=bucket.bucket_website_url,
                  export_name="GameCounterS3PublicUrl"
        )

        # EventBridge 毎日24:30に前日の集計を行うLambdaを実行
        events.Rule(
            self, "GameCounterEventRule",
            rule_name="GameCounterEventRule",
            schedule=events.Schedule.cron(
                minute="30",
                hour="15",
                day="*"),
            targets=[targets.LambdaFunction(create_log, retry_attempts=3)]
        )
