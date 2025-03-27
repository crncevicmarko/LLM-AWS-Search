from aws_cdk import (
    aws_apigateway as apigateway,
    Stack,
    aws_lambda as _lambda,
    aws_iam as iam, BundlingOptions, Duration,
    aws_secretsmanager as secretsmanager
)
import os
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
        
        

        lambda_role = iam.Role(
            self, "LambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
        )
        lambda_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
        )
        lambda_role.add_managed_policy(
        iam.ManagedPolicy.from_aws_managed_policy_name("AmazonAPIGatewayInvokeFullAccess")
        )
        lambda_role.add_managed_policy(
        iam.ManagedPolicy.from_aws_managed_policy_name("SecretsManagerReadWrite")
        )

        jira_secret = secretsmanager.Secret.from_secret_name_v2(self, "JiraSecret", "JIRA_CREDENTIALS")

       
      
        jira_secret.grant_read(lambda_role)
        
        request_layer = _lambda.LayerVersion(
            self, "RequestsLayer",
            code=_lambda.Code.from_asset("request-layer/request-layer.zip"),  # putanja do zip fajla
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
            description="Layer with requests module"
        )

        dotenv_layer = _lambda.LayerVersion(
            self, "DotEnvLayer",
            code=_lambda.Code.from_asset("dotenv-layer/dotenv-layer.zip"),  # putanja do zip fajla
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
            description="Layer with dotenv module"
        )
 

        def create_lambda_function(id, name, handler, include_dir, method, layers):
            function = _lambda.Function(
                self, id,
                function_name=name,
                runtime=_lambda.Runtime.PYTHON_3_9,
                layers=layers,
                handler=handler,
                code=_lambda.Code.from_asset(include_dir),
                memory_size=512,
                timeout=Duration.seconds(60),     
                environment={
                    "JIRA_SECRET_ARN": jira_secret.secret_arn,
                    "JIRA_URL" :'https://jiralevi9internship2025.atlassian.net/rest/api/2/search?jql=project=SCRUM',
                    "JIRA_EMAIL" :'grubor.masa@gmail.com'
                },
                role=lambda_role
            )
            return function

        get_tickets_lambda_function=create_lambda_function(
            "getTickets",  # id
            "getTicketsFunction",  # name
            "getTickets.lambda_handler",  # handler
            "backend/getTickets",  # include_dir
            "GET",  # method
            [request_layer,dotenv_layer]
        )

        get_tickets_integration = apigateway.LambdaIntegration(get_tickets_lambda_function) #integracija izmedju lambda fje i API gateway-a, sto znaci da API Gateway može pozivati Lambda funkciju kao odgovor na HTTP zahteve. 

        self.api.root.add_resource("getTickets").add_method("GET", get_tickets_integration, authorization_type=apigateway.AuthorizationType.NONE) 

















        # example resource
        # queue = sqs.Queue(
        #     self, "BackendQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )
