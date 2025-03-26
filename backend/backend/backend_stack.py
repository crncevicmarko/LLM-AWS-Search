from aws_cdk import (
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    Stack,

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
        get_user_input_lambda_func = _lambda.Function(
            self, "TestLambdaFunction",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.handler",
            code=_lambda.Code.from_asset("lambda"),
        )

        test_resource = self.api.root.add_resource("test-chatbot")
        test_resource.add_method("POST", apigateway.LambdaIntegration(get_user_input_lambda_func))
        # example resource
        # queue = sqs.Queue(
        #     self, "BackendQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )
