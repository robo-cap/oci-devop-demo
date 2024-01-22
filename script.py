import requests
import os
import re
import sys

#####################################################################################
# This script can be used in the build pipeline to push the pipeline                #
# execution status to GitHub.                                                       #
#                                                                                   #
# The parameters required to be defined at the pipeline level:                      #
# - githubToken                                                                     #
# - DEVOPS_PROJECT_ID                                                               #
#                                                                                   #
# Usage:                                                                            #
# python script.py <error|failure|pending|success>                                  #
#                                                                                   #
# More data: https://docs.github.com/en/rest/commits/statuses?apiVersion=2022-11-28 #
#####################################################################################



# Parameters required to be defined on the pipeline.
GITHUB_TOKEN = os.environ.get("githubToken")
DEVOPS_PROJECT_ID = os.environ.get("DEVOPS_PROJECT_ID", "DEFAULT")


# Parameteres available by default in the build stage
COMMIT_ID = os.environ.get("OCI_TRIGGER_COMMIT_HASH")
SOURCE_REPO = os.environ.get("OCI_TRIGGER_SOURCE_URL")

BUILD_PIPELINE_ID = os.environ.get("OCI_PIPELINE_ID")
BUILD_RUN_ID = os.environ.get("OCI_BUILD_RUN_ID")
REGION = os.environ.get("OCI_RESOURCE_PRINCIPAL_REGION")


if len(sys.argv) < 2:
    print("No status provided", file=sys.stderr)
    exit(1)
else:
    state = sys.argv[1]

match = re.match(r'https://github.com/([a-zA-Z0-9-]+)/([a-zA-Z0-9-]+)\.git', SOURCE_REPO)
if match:
    account, repo = re.match(r'https://github.com/([a-zA-Z0-9-]+)/([a-zA-Z0-9-]+)\.git', SOURCE_REPO).groups()
else:
    print(f"Invalid github repo: {SOURCE_REPO}", file=sys.stderr)
    exit(1)

r = requests.post(
    f'https://api.github.com/repos/{account}/{repo}/statuses/${COMMIT_ID}',
    headers={
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28"
    },
    json={
        'state': 'success',
        'target_url':f'https://cloud.oracle.com/devops-build/projects/{DEVOPS_PROJECT_ID}/build-pipelines/{BUILD_PIPELINE_ID}/build-runs/{BUILD_RUN_ID}?region={REGION}',
        'description': 'OCI DevOps pipeline execution status',
        'context': 'continuous-integration/oci-devops'
        }
    )

if r.status_code == 201:
    print("Pipeline status updated")
else:
    print(f"Pipeline status update failed with response {r.status_code}: {r.text}")