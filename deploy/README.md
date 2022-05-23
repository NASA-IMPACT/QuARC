
# Deployment Instructions

### Prerequisites:

- aws-cdk
- python
  
Make sure the stage you want to deploy to is exported to the ENV environment variable:

```bash
export ENV=<dev/stage/prod>
```

If this isn't set, `dev` is the default.

#### I: Create a virtual environment

```bash
python -m venv venv
```

#### II: Activate the virtual environment

```bash
source venv/bin/activate
```

#### III: Install dependencies

```bash
pip install -r requirements.txt
```

#### IV. View changes and deploy

```bash
cdk diff
cdk deploy
```

## Other useful cdk commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation
