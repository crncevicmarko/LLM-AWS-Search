from aws_cdk import (
    aws_secretsmanager as secretsmanager,
    aws_bedrock as bedrock,
    RemovalPolicy, 
    Duration,
    aws_apigateway as apigateway,
    Stack,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_iam as iam
)

from constructs import Construct

class BackendStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.api = apigateway.RestApi(self, "AIChatbotJiraAPI",
                                    rest_api_name="AI Chatbot Jira API",
                                    description="API for an AI chatbot retrieving data from Jira..",
                                    endpoint_types=[apigateway.EndpointType.REGIONAL], 
                                    default_cors_preflight_options={
                                        "allow_origins": apigateway.Cors.ALL_ORIGINS,
                                        "allow_methods": apigateway.Cors.ALL_METHODS, 
                                    }
                                    )


        # example resource
        # queue = sqs.Queue(
        #     self, "BackendQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )


        bucket = s3.Bucket(self, "my-bucket",
                   bucket_name="my-unique-bucket-name12312312311",
                   removal_policy=RemovalPolicy.DESTROY)


        pinecone_secrets = secretsmanager.Secret.from_secret_name_v2(self, "PineconeSecrets", "PINECONE_DB_SECRETS")

        lambda_role = iam.Role(self, "LambdaBedrockRole",
                               assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
                               managed_policies=[
                                   iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                                   iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3ReadOnlyAccess"),
                                   iam.ManagedPolicy.from_aws_managed_policy_name("AmazonBedrockFullAccess")
                               ])
        
        pinecone_secrets.grant_read(lambda_role)
        
        pinecone_layer = _lambda.LayerVersion(self, "PineconeLayer",
                                             code=_lambda.Code.from_asset("layer/pinecone.zip"),
                                             compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
                                             )
        
        setPineconeDB = _lambda.Function(self, "SetPineconeDB",
                                           runtime=_lambda.Runtime.PYTHON_3_9,
                                           handler="setPineconeDB.handler",
                                           code=_lambda.Code.from_asset("lambda"),
                                           role=lambda_role,
                                           timeout= Duration.minutes(5),
                                           environment={
                                               "PINECONE_SECRET_ARN": pinecone_secrets.secret_arn,
                                               "PINECONE_INDEX_NAME": "index-name",
                                           },
                                           layers=[pinecone_layer])
        