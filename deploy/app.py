#!/usr/bin/env python3
from aws_cdk import core

from deploy.deploy_stack import DeployStack


app = core.App()
DeployStack(app, "DeployStack",
)

app.synth()
