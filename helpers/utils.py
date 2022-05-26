import os
import boto3

ssm_client = boto3.client('ssm')

ssm_param_name = f"/quarc/{os.environ.get('ENV', 'dev')}/pyquarc/version"

def update_parameter(name, value):
    ssm_client.put_parameter(
        Name=name,
        Overwrite=True,
        Value=value,
    )

def get_parameter(name):
    parameter = ssm_client.get_parameter(Name=name)
    return parameter['Parameter']['Value']

