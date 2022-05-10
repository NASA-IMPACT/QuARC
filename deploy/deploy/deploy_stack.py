from aws_cdk import (
    core,
    aws_lambda_python as lambda_python_,
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
)

class DeployStack(core.Stack):

    def __init__(self, scope, construct_id, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        pyQuARC_layer = lambda_.LayerVersion(self, "pyQuARCLayer",
            code=lambda_.Code.from_asset("../layers/pyQuARC/"),
            compatible_architectures=[lambda_.Architecture.X86_64, lambda_.Architecture.ARM_64],
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_8],
        )

        pyQuARC_runner = lambda_python_.PythonFunction(self, "pyQuARCRunner",
            entry='../lambdas/runner/',
            runtime=lambda_.Runtime.PYTHON_3_8,
            index="handler.py",
            handler="handler",
            layers=[pyQuARC_layer]
        )

        # TODO: Give permission to invoke the lambda function
        api = apigateway.LambdaRestApi(self, "pyQuARCAPI",
            handler=pyQuARC_runner,
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS
            )
        )

        validate = api.root.add_resource("validate")
        validate.add_method("POST")
