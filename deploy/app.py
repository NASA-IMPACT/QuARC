#!/usr/bin/env python3

from config import APP_NAME, ENV

from aws_cdk import core

from deploy.stack import AppStack


app = core.App()
AppStack(app, f"{APP_NAME}-{ENV}",
)

app.synth()
