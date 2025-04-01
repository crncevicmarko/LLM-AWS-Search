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
        
        self.api = apigateway.RestApi(
                self, 
                "AIChatbotJiraAPI",
                rest_api_name="AI Chatbot Jira API",
                description="API for an AI chatbot retrieving data from Jira.",
                endpoint_types=[apigateway.EndpointType.REGIONAL], 
                default_cors_preflight_options={
                    "allow_origins": apigateway.Cors.ALL_ORIGINS,  
                    "allow_methods": apigateway.Cors.ALL_METHODS,  
                    "allow_headers": ["*"],  
                    "allow_credentials": True  
                }
                )
        
        
        lambda_role = iam.Role(self, "LambdaRole",
                               assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
                               managed_policies=[
                                   iam.ManagedPolicy.from_aws_managed_policy_name("SecretsManagerReadWrite"),
                                    iam.ManagedPolicy.from_aws_managed_policy_name("AmazonAPIGatewayInvokeFullAccess"),
                                   iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                                   iam.ManagedPolicy.from_aws_managed_policy_name("AmazonBedrockFullAccess")
                               ])
        
        jira_secret = secretsmanager.Secret.from_secret_name_v2(self, "JiraSecret", "JIRA_CREDENTIALS")
        jira_secret.grant_read(lambda_role)
        
        pinecone_secrets = secretsmanager.Secret.from_secret_name_v2(self, "PineconeSecrets", "PINECONE_DB_SECRETS")
        pinecone_secrets.grant_read(lambda_role)

        request_layer = _lambda.LayerVersion(
            self, "RequestsLayer",
            code=_lambda.Code.from_asset("layers/requests.zip"),  
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
            description="Layer with requests module"
        )

        pinecone_layer = _lambda.LayerVersion(
            self, "PineconeLayer",
            code=_lambda.Code.from_asset("layers/pinecone.zip"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
        )
 

        def create_lambda_function(id, handler, include_dir, method, layers, environment):
            function = _lambda.Function(
                self, id,
                runtime=_lambda.Runtime.PYTHON_3_9,
                layers=layers,
                handler=handler,
                code=_lambda.Code.from_asset(include_dir),
                memory_size=512,
                timeout=Duration.seconds(60),     
                environment = environment,
                role=lambda_role
            )
            return function

        get_tickets_lambda_function=create_lambda_function(
            "SaveIssues",  
            "saveIssues.handler",  
            "lambda",  
            "GET",  
            [request_layer, pinecone_layer],
            {
                "JIRA_SECRET_ARN": jira_secret.secret_arn,
                "JIRA_URL" :'https://jiralevi9internship2025.atlassian.net/rest/api/2/search?jql=project=SCRUM',
                "JIRA_EMAIL" :'grubor.masa@gmail.com',
                "JIRA_URL_COMMENTS": 'https://jiralevi9internship2025.atlassian.net/rest/api/2/search?jql=project=SCRUM&maxResults=100&fields=comment',
                "PINECONE_SECRET_ARN": pinecone_secrets.secret_arn,
            }
        )

        get_user_input_lambda_func = _lambda.Function(
            self, "TestLambdaFunction",
            runtime=_lambda.Runtime.PYTHON_3_9,
            layers=[pinecone_layer],
            handler="retreveUserInput.handler",
            code=_lambda.Code.from_asset("lambda"),
            role=lambda_role,
            memory_size=512, 
            timeout=Duration.seconds(60),
            environment={  
                "PINECONE_SECRET_ARN": pinecone_secrets.secret_arn,
            }
        )

        get_tickets_integration = apigateway.LambdaIntegration(get_tickets_lambda_function)  
        get_user_input_integration = apigateway.LambdaIntegration(get_user_input_lambda_func)


        self.api.root.add_resource("SaveIssues").add_method("GET", get_tickets_integration, authorization_type=apigateway.AuthorizationType.NONE) 
        get_user_input = self.api.root.add_resource("test-chatbot")
        get_user_input.add_method("POST", get_user_input_integration, authorization_type=apigateway.AuthorizationType.NONE)

        lambda_role = iam.Role(self, "LambdaBedrockRole",
                               assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
                               managed_policies=[
                                   iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                                   iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3ReadOnlyAccess"),
                                   iam.ManagedPolicy.from_aws_managed_policy_name("AmazonBedrockFullAccess"),
                                   iam.ManagedPolicy.from_aws_managed_policy_name("SecretsManagerReadWrite") 
                               ])
        
        setPineconeDB = create_lambda_function(
            "SetPineconeDB",
            "setPineconeDB.handler",
            "lambda",
            "PUT",
            [pinecone_layer],
            {
                "PINECONE_SECRET_ARN": pinecone_secrets.secret_arn,
            }
        )


        jiraWebHookFunction = create_lambda_function(
            "jiraWebhookFunction",
            "jiraWebhookHandler.lambda_handler",
            "lambda",
            "POST",
            [pinecone_layer,request_layer],
            {
                "PINECONE_SECRET_ARN": pinecone_secrets.secret_arn,
                    "PINECONE_INDEX_NAME": "index-name",
                    "JIRA_SECRET_ARN": jira_secret.secret_arn,
                    "JIRA_URL" :'https://jiralevi9internship2025.atlassian.net/rest/api/2/search?jql=project=SCRUM',
                    "JIRA_EMAIL" :'grubor.masa@gmail.com',
                    "JIRA_URL_COMMENTS": 'https://jiralevi9internship2025.atlassian.net/rest/api/2/search?jql=project=SCRUM&maxResults=100&fields=comment'
            }
        )

        jira_webhook_integration = apigateway.LambdaIntegration(jiraWebHookFunction)
        self.api.root.add_resource("jiraWebhookHandler").add_method("POST", jira_webhook_integration, authorization_type=apigateway.AuthorizationType.NONE) 



        