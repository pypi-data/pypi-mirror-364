import os
import urllib.request
import zipfile
import json


RELEASES_URL = "https://api.github.com/repos/akarabaev/interactive-dtree-fe/releases"
RELEASE_TAG = 'test2'
ASSET_NAME = 'react-app-test2.zip'
ZIP_PATH = 'frontend.zip'


def fetch_frontend_assets():
    # github_token = os.environ['GITHUB_TOKEN']
    github_token = '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'
    
    # First, get the release information to find the asset ID
    release_url = f"{RELEASES_URL}/tags/{RELEASE_TAG}"
    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': f'Bearer {github_token}',
    }
    
    # Create a request with headers
    req = urllib.request.Request(release_url, headers=headers)
    
    with urllib.request.urlopen(req) as response:
        release_data = json.loads(response.read().decode())
        
    # Find the asset with the specified name
    asset_id = None
    for asset in release_data.get('assets', []):
        if asset['name'] == ASSET_NAME:
            asset_id = asset['id']
            break
    
    if not asset_id:
        raise Exception(f"Asset '{ASSET_NAME}' not found in release '{RELEASE_TAG}'")
    
    print(f"Found asset ID: {asset_id}")
    
    asset_url = f"{RELEASES_URL}/assets/{asset_id}"
    asset_headers = {
        'Accept': 'application/octet-stream',
        'Authorization': f'Bearer {github_token}',
    }
    
    asset_req = urllib.request.Request(asset_url, headers=asset_headers)
    
    print(f"Downloading asset from: {asset_url}")
    with urllib.request.urlopen(asset_req) as response:
        with open(ZIP_PATH, 'wb') as f:
            f.write(response.read())
    
    print(f"Downloaded {ZIP_PATH}")


def unpack_frontend_assets():
    with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
        zip_ref.extractall("app/")

    os.remove(ZIP_PATH)


def test_sanity():
    fetch_frontend_assets()
    unpack_frontend_assets()
