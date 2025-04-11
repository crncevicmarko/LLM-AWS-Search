from aws_cdk import (
    aws_secretsmanager as secretsmanager,
    Duration,
    aws_apigateway as apigateway,
    Stack,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_cognito as cognito,
    aws_dynamodb as dynamodb
)

from constructs import Construct
import shutil

class BackendStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        JIRA_URL_BASE = 'https://jiralevi9internship2025.atlassian.net/rest/api/2/search?jql=project=SCRUM&maxResults=100&'
        JIRA_URL = 'https://jiralevi9internship2025.atlassian.net/rest/api/2/search?jql=project=SCRUM&maxResults=1000'
        JIRA_URL_COMMENTS = 'https://jiralevi9internship2025.atlassian.net/rest/api/2/search?jql=project=SCRUM&maxResults=1000&fields=comment'
        JIRA_EMAIL = 'grubor.masa@gmail.com'
        PINECONE_INDEX_URL = 'https://index-name-cj2bvvd.svc.aped-4627-b74a.pinecone.io'
        
        user_pool = cognito.UserPool(
            self, "JiraUserPool",
            user_pool_name="JIraUserPool",
            self_sign_up_enabled=True,  
            auto_verify=cognito.AutoVerifiedAttrs(email=True), 
            password_policy=cognito.PasswordPolicy(
                min_length=8,
                require_digits=True,
                require_lowercase=True,
                require_uppercase=True,
                require_symbols=False
                ),
            sign_in_aliases=cognito.SignInAliases(email=True),
            account_recovery=cognito.AccountRecovery.EMAIL_ONLY,
            standard_attributes=cognito.StandardAttributes(
                email=cognito.StandardAttribute(required=True)
            )
        )

        user_pool_client = cognito.UserPoolClient(
            self, "JiraUserPoolClient",
            user_pool=user_pool,
            generate_secret=False,  
            id_token_validity=Duration.hours(2),          
            access_token_validity=Duration.hours(2),      
            refresh_token_validity=Duration.days(30),
            auth_flows=cognito.AuthFlow(
                user_password=True,  
                user_srp=True  
            ),
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(authorization_code_grant=True),
                callback_urls=["http://localhost:4200"],  
                logout_urls=["http://localhost:4200"]
            )
        )

        authorizer_layer = _lambda.LayerVersion(
            self, "AuthorizerLayer",
            code=_lambda.Code.from_asset("layers/authorizer.zip"),
            compatible_runtimes=[_lambda.Runtime.NODEJS_18_X]
        )

        auth_lambda = _lambda.Function(self, "AuthLambda",
            code=_lambda.Code.from_asset("lambda/authentication"),
            handler="auth.handler",  
            runtime=_lambda.Runtime.NODEJS_18_X,
            layers=[authorizer_layer],
            environment={
                "USER_POOL_ID" : user_pool.user_pool_id,  
                "CLIENT_ID" : user_pool_client.user_pool_client_id, 
            }
        )

        lambda_authorizer = apigateway.TokenAuthorizer(
            self, 
            "LambdaAuthorizer",  
            handler=auth_lambda, 
        )
        
        self.api = apigateway.RestApi(
                self, 
                "AIChatbotJiraAPI",
                rest_api_name="AI Chatbot Jira API",
                description="API for an AI chatbot retrieving data from Jira.",
                endpoint_types=[apigateway.EndpointType.REGIONAL], 
                default_cors_preflight_options={
                    "allow_origins": ["http://localhost:4200","https://dlg9vobdrudc.cloudfront.net"],
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
        
        register_user_lambda_function=create_lambda_function(
            "Register",
            "register.handler",
            "lambda/register",
            "POST",
            [request_layer],
            {
                "USER_POOL_ID":user_pool.user_pool_id,
                "CLIENT_ID":user_pool_client.user_pool_client_id
            }
        )

        email_confirmation=create_lambda_function(
            "ConfirmEmail",
            "confirmation.handler",
            "lambda/confirmation",
            "POST",
            [request_layer],
            {
                "USER_POOL_ID":user_pool.user_pool_id,
                "CLIENT_ID":user_pool_client.user_pool_client_id
            }
        )

        save_issues = create_lambda_function(
            "SaveIssues",  
            "saveIssues.handler",  
            "lambda/saveIssues",  
            "GET",  
            [request_layer, pinecone_layer],
            {
                "JIRA_SECRET_ARN": jira_secret.secret_arn,
                "JIRA_URL" : JIRA_URL_BASE,
                "JIRA_EMAIL" : JIRA_EMAIL,
                "JIRA_URL_COMMENTS": JIRA_URL_COMMENTS,
                "PINECONE_INDEX_URL": PINECONE_INDEX_URL,
                "PINECONE_SECRET_ARN": pinecone_secrets.secret_arn,
            }
        )

        get_user_input_lambda_func = _lambda.Function(
            self, "RetrieveUserInput",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="retrieveUserInput.handler",
            layers=[pinecone_layer],
            code=_lambda.Code.from_asset("lambda/retrieveUserInput"),
            role=lambda_role,
            memory_size=512, 
            timeout=Duration.seconds(60),
            environment={  
                "PINECONE_SECRET_ARN": pinecone_secrets.secret_arn,
                "PINECONE_INDEX_URL": PINECONE_INDEX_URL,
            }
        )

        get_tickets_integration = apigateway.LambdaIntegration(save_issues  )  
        get_user_input_integration = apigateway.LambdaIntegration(get_user_input_lambda_func)


        self.api.root.add_resource("SaveIssues").add_method("GET", get_tickets_integration, authorization_type=apigateway.AuthorizationType.NONE) 
        get_user_input = self.api.root.add_resource("test-chatbot")

        get_user_input.add_method("POST", get_user_input_integration, 
            authorization_type=apigateway.AuthorizationType.CUSTOM,
            authorizer=lambda_authorizer)

        lambda_role = iam.Role(self, "LambdaBedrockRole",
                               assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
                               managed_policies=[
                                   iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                                   iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3ReadOnlyAccess"),
                                   iam.ManagedPolicy.from_aws_managed_policy_name("AmazonBedrockFullAccess"),
                                   iam.ManagedPolicy.from_aws_managed_policy_name("SecretsManagerReadWrite") 
                               ])


        jiraWebHookFunction = create_lambda_function(
            "jiraWebhookFunction",
            "jiraWebhookHandler.handler",
            "lambda/jiraWebHook",
            "POST",
            [pinecone_layer,request_layer],
            {
                "PINECONE_SECRET_ARN": pinecone_secrets.secret_arn,
                "PINECONE_INDEX_URL" : PINECONE_INDEX_URL,
                "PINECONE_INDEX_NAME": "index-name",
                "JIRA_SECRET_ARN": jira_secret.secret_arn,
                "JIRA_URL" : JIRA_URL,
                "JIRA_EMAIL" : JIRA_EMAIL,
                "JIRA_URL_COMMENTS": JIRA_URL_COMMENTS
            }
        )

        jira_webhook_integration = apigateway.LambdaIntegration(jiraWebHookFunction)
        self.api.root.add_resource("jiraWebhookHandler").add_method("POST", jira_webhook_integration, authorization_type=apigateway.AuthorizationType.NONE) 


        registration_integration=apigateway.LambdaIntegration(register_user_lambda_function)
        self.api.root.add_resource("register").add_method("POST", registration_integration,authorization_type=apigateway.AuthorizationType.NONE)
        


        confirmation_integration=apigateway.LambdaIntegration(email_confirmation)
        self.api.root.add_resource("confirm").add_method("POST",confirmation_integration,authorization_type=apigateway.AuthorizationType.NONE)
        

        chat_table = dynamodb.Table(
            self,
            "ChatHistory",
            partition_key=dynamodb.Attribute(name="chat_id", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="timestamp", type=dynamodb.AttributeType.NUMBER),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )
        chat_titles = dynamodb.Table(
            self,
            "ChatTitles",
            partition_key=dynamodb.Attribute(name="chat_id", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )
        save_message_lambda = create_lambda_function(
            "SaveChatMessageLambda",
            "saveChatMessage.handler",
            "lambda/saveChatMessage",
            "POST",
            [],
            {
                "TABLE_NAME": chat_table.table_name
            }

        )

        get_messages_by_id = create_lambda_function(
            "getChatLambda",
            "getMessagesByChatId.handler",
            "lambda/getMessagesByChat",
            "GET",
            [],
            {
                "TABLE_NAME": chat_table.table_name
            }

        )
        chat_table.grant_write_data(save_message_lambda)
        chat_table.grant_read_data(get_messages_by_id)

        get_title_by_id_lambda = create_lambda_function(
            "GetTitleByIdLambda",
            "getChatTitles.handler",  
            "lambda",  
            "GET",  
            [],  
            {
                "TABLE_NAME": chat_titles.table_name  
            }
        )


        save_message_resource = self.api.root.add_resource("save-message")
        save_message_resource.add_method(
            "POST", apigateway.LambdaIntegration(save_message_lambda),
            authorization_type=apigateway.AuthorizationType.CUSTOM,
            authorizer=lambda_authorizer
        )

        get_messages_resource = self.api.root.add_resource("get-messages")
        get_messages_resource.add_method(
            "GET", apigateway.LambdaIntegration(get_messages_by_id),
            authorization_type=apigateway.AuthorizationType.CUSTOM,
            authorizer=lambda_authorizer
        )
        title_generation_lambda = _lambda.Function(
            self, "TitleGenerationLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="generateTitle.handler",
            code=_lambda.Code.from_asset("lambda/generateTitle"),
            memory_size=512,
            timeout=Duration.seconds(60),
            environment={
                "TABLE_NAME": chat_titles.table_name  
            }
        )

        chat_titles.grant_write_data(title_generation_lambda)

        title_generation_integration = apigateway.LambdaIntegration(title_generation_lambda)

        self.api.root.add_resource("generate-title").add_method("POST", title_generation_integration)

        get_title_by_id_lambda = create_lambda_function(
            "GetTitleByIdLambda",
            "getChatTitles.handler",  
            "lambda/getChatTitles",  
            "GET",  
            [],  
            {
                "TABLE_NAME": chat_titles.table_name  
            }
        )

        chat_titles.grant_read_data(get_title_by_id_lambda)

        get_title_integration = apigateway.LambdaIntegration(get_title_by_id_lambda)

        self.api.root.add_resource("get-title").add_method("GET", get_title_integration)


        get_chats_by_userid = _lambda.Function(
            self, "getChatByUserLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="getChatsByUserId.handler",
            code=_lambda.Code.from_asset("lambda"),
            memory_size=512,
            timeout=Duration.seconds(60),
            environment={
                "TABLE_NAME": chat_titles.table_name  # Use the correct table here
            }
        )       

        chat_titles.grant_read_data(get_chats_by_userid)

        get_chats_by_userid.add_to_role_policy(
            statement=iam.PolicyStatement(
                actions=["logs:*", "dynamodb:Scan"],  
                resources=["*"]  
            )
        )



        # get_chats_by_userid_integration = apigateway.LambdaIntegration(get_chats_by_userid)

        # self.api.root.add_resource("chats-by-user").add_cors_preflight(
        # allow_origins=["*"],  # This is the allowed origin (change it if needed)
        # allow_methods=["GET", "POST", "PUT", "DELETE"],  # Allowed HTTP methods
        # allow_headers=["Content-Type", "Authorization"],  # Allowed headers
        # max_age=Duration.days(1)  # Cache preflight response for 1 day
        # ).add_method("GET",get_chats_by_userid_integration)

        get_chat_history_resource = self.api.root.add_resource("chats-by-user")
        get_chat_history_resource.add_method(
            "GET", apigateway.LambdaIntegration(get_chats_by_userid),
            authorization_type=apigateway.AuthorizationType.CUSTOM,
            authorizer=lambda_authorizer
        )
 

        # Create the resource for 'chats-by-user'
        # self.api.root.add_resource("chats-by-user").add_method("GET", get_chats_by_userid_integration)

        
        sendBugReport = _lambda.Function(
            self, "sendBugReport",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="sendBugReport.handler",
            code=_lambda.Code.from_asset("lambda/sendBugReport"),
            memory_size=512,
            timeout=Duration.seconds(60),

        )

        sendBugReport.add_to_role_policy(
        iam.PolicyStatement(
            actions=["ses:SendEmail"],
            resources=[
                "arn:aws:ses:eu-west-1:785202558517:identity/grubor.masa@gmail.com",  # Sender Email
                "arn:aws:ses:eu-west-1:785202558517:identity/dobrosavtufegdzic@gmail.com"  # Recipient Email
            ]
        )
)
        
        sendBugReport.add_to_role_policy(
    iam.PolicyStatement(
        actions=["bedrock:InvokeModel"],
        resources=[
            "arn:aws:bedrock:eu-west-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0"  # Specific Bedrock model
        ]
    )
)

        sendBugReport_integration = apigateway.LambdaIntegration(sendBugReport)

        self.api.root.add_resource("send-bug-report").add_method("POST", sendBugReport_integration)

