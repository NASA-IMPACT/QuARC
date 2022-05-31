import io, os, requests, sys, zipfile

from utils import get_parameter, ssm_param_name

OWNER = "NASA-IMPACT"
REPO = "pyQuARC"

API_URL = f"https://api.github.com/repos/{OWNER}/{REPO}/releases/latest"


def api_response(url):
    """
    Returns the response from the API, raises exception if not 200
    """
    response = requests.get(url)
    response.raise_for_status()
    return response


def latest_release(response):
    """
    Returns the tagname and URL of the latest release.
    """
    response = response.json()
    return response["tag_name"], response["zipball_url"]


def install(zip_file):
    """
    Installs the latest pyQuARC release into the layers folder
    """
    zip_file.extractall("tmp/")
    # Get the first directory in the list (folder name is pyQuARC<SOMEHASH>)
    directory = [x for x in os.listdir("tmp/") if os.path.isdir(f"tmp/{x}")][0]
    return os.system(f"pip install tmp/{directory} --target=layers/pyQuARC/python")


if __name__ == "__main__":
    force = "--force" in sys.argv
    curr_version = get_parameter(ssm_param_name)

    response = api_response(API_URL)
    version, zipball_url = latest_release(response)

    if (version != curr_version) or force:
        zip_response = api_response(zipball_url)
        zip_file = zipfile.ZipFile(io.BytesIO(zip_response.content))

        failure = install(zip_file)

        if failure:
            raise Exception(f"Failed to update pyQuARC to the latest version {version}")

        # If the installation succeeds, set required env variables to be used in next steps
        env_file = os.environ.get("GITHUB_ENV")

        with open(env_file, "a") as myfile:
            myfile.write(f"NEW_VERSION={version}")
