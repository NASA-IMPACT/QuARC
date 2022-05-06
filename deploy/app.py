#!/usr/bin/env python3
import aws_cdk as cdk

from deploy.deploy_stack import DeployStack


app = cdk.App()
DeployStack(app, "DeployStack",
    )

app.synth()
