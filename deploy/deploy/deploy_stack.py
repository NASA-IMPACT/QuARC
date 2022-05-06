from aws_cdk import (
    Stack,
    aws_lambda_python as lambda_python_,
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
)

class DeployStack(Stack):

    def __init__(self, scope, construct_id, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        pyQuARC_layer = lambda_.LayerVersion(self, "pyQuARCLayer",
            code=lambda_.Code.from_asset("../layers/pyQuARC/"),
            compatible_architectures=[lambda_.Architecture.X86_64, lambda_.Architecture.ARM_64]
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
            handler=pyQuARC_runner
        )

        pyQuARC_runner.grant_invoke(api.root.role)

        validate = api.root.add_resource("validate")
        validate.add_method("POST")
