import requests, zipfile, io, os

from utils import get_parameter, ssm_param_name

OWNER = "NASA-IMPACT"
REPO = "pyQuARC"

API_URL = f"https://api.github.com/repos/{OWNER}/{REPO}/releases/latest"

response = requests.get(API_URL)
response.raise_for_status()

response = response.json()
version = response.get("tag_name", "v1.0.0")

# Get the current version being used by QuARC
curr_version = get_parameter(ssm_param_name)

if version != curr_version:
    # Zip of the latest release
    zip_url = response["zipball_url"]

    zip_response = requests.get(zip_url)
    zip_response.raise_for_status()
    zip_file = zipfile.ZipFile(io.BytesIO(zip_response.content))

    # Extract the zip file to the tmp/ directory
    zip_file.extractall("tmp/")

    # Get the first directory in the list (folder name is pyQuARC<SOMEHASH>)
    directory = [x for x in os.listdir('tmp/') if os.path.isdir(f"tmp/{x}")][0]

    # Run pyQuARC installation
    return_code = os.system(f"pip install tmp/{directory} --target=layers/pyQuARC/python")

    if return_code == 0:
        # If the installation succeeds, set required env variables to be used in next steps
        env_file = os.environ.get('GITHUB_ENV')

        with open(env_file, "a") as myfile:
            myfile.write("NEEDS_DEPLOYMENT=true\n")
            myfile.write(f"NEW_VERSION={version}")
    else:
        raise Exception("Failed to update pyQuARC")
