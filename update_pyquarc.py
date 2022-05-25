import requests, zipfile, io, os
import boto3


ssm_client = boto3.client('ssm')


def get_parameter(name):
    parameter = ssm_client.get_parameter(Name=name)
    return parameter['Parameter']['Value']

def update_parameter(name, value):
    ssm_client.put_parameter(
        Name=name,
        Overwrite=True,
        Value=value,
    )

owner = "NASA-IMPACT"
repo = "pyQuARC"
ssm_param_name = f"/quarc/{os.environ.get('ENV', 'dev')}/pyquarc/version"

api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
response = requests.get(api_url).json()
version = response.get("tag_name", "v1.0.0")[1:]

current_pyquarc_version = get_parameter(ssm_param_name)

if version != current_pyquarc_version:
    zip_url = response["zipball_url"]
    zip_response = requests.get(zip_url)
    zip_file = zipfile.ZipFile(io.BytesIO(zip_response.content))
    zip_file.extractall("tmp/")
    directory = [x for x in os.listdir('tmp/') if os.path.isdir(f"tmp/{x}")][0]
    return_code = os.system(f"pip install tmp/{directory} --target=layers/pyQuARC/python")

    if return_code == 0:
        update_parameter(ssm_param_name, version)
        os.system(f"echo NEEDS_DEPLOYMENT=true >> $GITHUB_ENV")
    else:
        print("Failed to update pyQuARC")
