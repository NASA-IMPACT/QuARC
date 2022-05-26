import requests, zipfile, io, os

from utils import get_parameter, ssm_param_name

owner = "NASA-IMPACT"
repo = "pyQuARC"

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
        env_file = os.environ.get('GITHUB_ENV')

        with open(env_file, "a") as myfile:
            myfile.write("NEEDS_DEPLOYMENT=true\n")
            myfile.write(f"NEW_VERSION={version}")
    else:
        print("Failed to update pyQuARC")
