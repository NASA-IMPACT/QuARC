import config

from aws_cdk import (
    core,
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
        runner = lambda_.Function(
            self,
            f"{construct_id}-runner",
            code=lambda_.Code.from_asset("../lambdas/runner/"),
            runtime=lambda_.Runtime.PYTHON_3_8,
            handler="handler.handler",
            layers=[pyQuARC_layer],
            function_name=f"{construct_id}-runner",
        )

        # The API Gateway that the integrates with the lambda function, where clients can submit requests
        api = apigateway.LambdaRestApi(
            self,
            f"{construct_id}-api",
            handler=runner,
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS, allow_methods=apigateway.Cors.ALL_METHODS
            ),
            deploy_options=apigateway.StageOptions(
                stage_name=config.ENV,
            ),
            rest_api_name=f"{construct_id}-api",
        )

        validate = api.root.add_resource("validate")
        validate.add_method("POST")
