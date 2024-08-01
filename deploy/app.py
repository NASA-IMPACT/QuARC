#!/usr/bin/env python3

from config import APP_NAME, ENV

from aws_cdk import App

from deploy.stack import AppStack


app = App()
AppStack(app, f"{APP_NAME}-{ENV}")

app.synth()
