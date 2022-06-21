import config

from aws_cdk import (
    core,
    aws_lambda_python as lambda_python_,
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
)


class AppStack(core.Stack):
    """
    Stack that deploys the API Gateway and Lambda functions and layers.
    """

    def __init__(self, scope, construct_id, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # The Lambda layer that holds pyQuARC. This layer will be used by the lambda function
        pyQuARC_layer = lambda_.LayerVersion(
            self,
            f"{construct_id}-pyQuARC-layer",
            code=lambda_.Code.from_asset("../layers/pyQuARC/"),
            compatible_architectures=[lambda_.Architecture.X86_64, lambda_.Architecture.ARM_64],
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_8],
            layer_version_name=f"{construct_id}-pyQuARC-layer",
        )

        # The lambda that actually runs pyQuARC and the validation that it performs

        runner = lambda_python_.PythonFunction(
            self,
            f"{construct_id}-runner",
            entry="../lambdas/runner/",
            runtime=lambda_.Runtime.PYTHON_3_8,
            index="handler.py",
            handler="handler",
            layers=[pyQuARC_layer],
            function_name=f"{construct_id}-runner",
        )

        # The API Gateway that the integrates with the lambda function, where clients can submit requests
        api = apigateway.RestApi(
            self,
            f"{construct_id}-api",
            deploy_options=apigateway.StageOptions(
                stage_name=config.ENV,
            ),
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS, allow_methods=apigateway.Cors.ALL_METHODS
            ),
            rest_api_name=f"{construct_id}-api",
            binary_media_types=["*/*"],
        )
        # api = apigateway.LambdaRestApi(
        #     self,
        #     f"{construct_id}-api",
        #     handler=runner,
        #     proxy=False,
        #     default_cors_preflight_options=apigateway.CorsOptions(
        #         allow_origins=apigateway.Cors.ALL_ORIGINS, allow_methods=apigateway.Cors.ALL_METHODS
        #     ),
        #     deploy_options=apigateway.StageOptions(
        #         stage_name=config.ENV,
        #     ),
        #     rest_api_name=f"{construct_id}-api",
        #     binary_media_types=["*/*"],
        # )

        validate = api.root.add_resource("validate")
        request_model = api.add_model(
            "RequestModel",
            content_type="application/json",
            model_name="RequestModel",
            schema=apigateway.JsonSchema(
                schema=apigateway.JsonSchemaVersion.DRAFT4,
                title="pollRequest",
                type=apigateway.JsonSchemaType.OBJECT,
                properties={
                    "format": apigateway.JsonSchema(type=apigateway.JsonSchemaType.STRING),
                    "concept_id": apigateway.JsonSchema(type=apigateway.JsonSchemaType.STRING)
                    # "file": apigateway.JsonSchema(type=apigateway.JsonSchemaType.OBJECT)
                },
                required=["format"],
            ),
        )

        req_validator = api.add_request_validator(
            "apiReqValidator", validate_request_parameters=True, validate_request_body=True
        )

        # resp_template = """$input.path('$.body')"""
        greetApiIntegration = apigateway.LambdaIntegration(
            handler=runner,
            proxy=False,
            # passthrough_behavior=apigateway.PassthroughBehavior.NEVER,
            # integration_responses=[
            #     apigateway.IntegrationResponse(
            #         status_code="200",
            #         # selection_pattern="2\d{2}",  # Use for mapping Lambda Errors
            #         response_parameters={
            #             "method.response.header.Access-Control-Allow-Headers": "'cache-control,Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
            #             "method.response.header.Content-Type": "'application/json'",
            #         },
            #         response_templates={"application/json": f"{resp_template}"},
            #     )
            # ],
        )

        # Because this is NOT a proxy integration, we need to define our response model
        response_model = api.add_model(
            "ResponseModel",
            content_type="application/json",
            model_name="MiztiikResponseModel",
            schema=apigateway.JsonSchema(
                schema=apigateway.JsonSchemaVersion.DRAFT4,
                title="updateResponse",
                type=apigateway.JsonSchemaType.OBJECT,
                properties={
                    "message": apigateway.JsonSchema(type=apigateway.JsonSchemaType.STRING)
                },
            ),
        )

        validate.add_method(
            "POST",
            integration=greetApiIntegration,
            request_validator=req_validator,
            request_models={"application/json": request_model},
            method_responses=[
                apigateway.MethodResponse(
                    status_code="200",
                    response_parameters={
                        "method.response.header.Content-Type": True,
                        "method.response.header.Access-Control-Allow-Headers": True,
                    },
                    response_models={"application/json": response_model},
                ),
                apigateway.MethodResponse(
                    status_code="400",
                    response_parameters={
                        "method.response.header.Content-Length": True,
                    },
                    response_models={"application/json": apigateway.EmptyModel()},
                ),
            ],
        )
