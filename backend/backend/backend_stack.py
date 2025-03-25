from aws_cdk import (
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


        # example resource
        # queue = sqs.Queue(
        #     self, "BackendQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )
