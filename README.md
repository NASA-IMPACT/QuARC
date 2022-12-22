# QuARC: PyQuARC as a service

[PyQuARC](https://github.com/NASA-IMPACT/pyquarc) is an open source library for Earth Observation metadata quality assessment.

Learn more in the linked [Github repo](https://github.com/NASA-IMPACT/pyquarc).

QuARC is a service built on top of pyQuARC to provide easily accessible metadata quality assessment.

## Try it out
https://quarc.nasa-impact.net/docs/

## Endpoints
`/validate`

This api reads and evaluates descriptive metadata used to catalog Earth observation data products and files.

**Supported Content-types:** `multipart/form-data` and `application/json`
### Arguments
| Parameter                 | Type       | Description   |	
| :------------------------ |:-------------:| :-------------|
|`concept_id `	       |	string           |Identifier of collections (You can also pass list of concept ids separated by commas). For example: "C1214470488-ASF, C123456-LPDAAC_ECS"
| `format  `        | string           |format of the collections (supported formats : `echo-c`,  `echo-g`, `dif10`, `umm-c`, `umm-g`)
| `file	`       |	file	            |Binary file object of metadata file. **Note**: Be sure to set `multipart/formdata` as a content type in headers when uplaoding files.
| `cmr_query	`       |	string	            |This CMR query URL is used for obtaining a list of concept ids and iterating through each collections from the list for assesssing the metadata. For example: https://cmr.uat.earthdata.nasa.gov/search/collections?keyword=csda
| `auth_key`	       |	string	            |Authorization bearer key if required. For certain environment, we need to pass **Authorization: Bearer** header for downloading metadata from CMR. The token will only authorize for applications that are EDL compliant and do not have unapproved EULAs. You can obtain it from EDL page by following the steps [here](https://urs.earthdata.nasa.gov/documentation/for_users/user_token).
| `cmr_host	`       |	string	            |(Default: https://cmr.earthdata.nasa.gov ) CMR host URL for downloading metadata. This URL acts as a base URL for downloading metadata. For example: https://cmr.uat.earthdata.nasa.gov/search/ This is CMR URL for UAT environment.

## Using the API with python
```
QUARC_API = "//specify_quarc_api_here"
CMR_HOST = "//specify_cmr_host_here_uses_default_cmr_if_not_specified"
import requests
TOKEN = "//specify_token_if_needed"  
headers = {"content-type": "application/json"}
payload = {
    "format": "echo-c",
    "cmr_host": CMR_HOST,
    "auth_key": TOKEN,
    "concept_id": "C1240487597-CSDA",
}
response = requests.post(
    QUARC_API,
    data=json.dumps(payload),
    headers=headers,
)
```

If you want to use files instead of concept_ids
```

QUARC_API = "//specify_quarc_api_here"
with open('file_name', 'rb') as f:
    payload = {
        "format": "echo-c"
    }
    response = requests.post(   
        QUARC_API,
        data=payload,
        files = {"file": f}
    )
result = response.json()
print(result)
```

## Code Formatting and Linting

This project enforces linting and formatting upon pull requests via Github Actions. Formatter and linter config files are included in the repo, and users are encouraged to enable auto-formatting in their code editor, which should automatically use the included configs.

Necessary Python libraries can be installed with `requirements_dev.txt`.

For further details on team coding standards which are not automatically checked by Github Actions, please read the [conventions document](https://docs.google.com/document/d/1b0YSCObQu3yvWeblHDDeIKzapxUkuVQVElGw_rxrC4Q/view).

### Python

For python, this project uses [Black](https://black.readthedocs.io/en/stable/) for formatting and [Flake8](https://flake8.pycqa.org/en/latest/) for linting. Configurations are in the following locations:

- [Black configuration](pyproject.toml)
- [Flake8 configuration](tox.ini)
- [Github action](.github/workflows/lint.yml) for linting and formatting check
