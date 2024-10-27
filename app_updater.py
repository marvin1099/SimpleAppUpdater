#!/usr/bin/env python

import os
import sys
import json
import requests
import re
from pathlib import Path
import subprocess

# Determine the base directory and config file path based on execution mode
if getattr(sys, 'frozen', False):
    # Compiled executable
    script = Path(sys.executable)
    args = sys.argv[:]
else:
    # Running as a script
    script = Path(__file__)
    args = sys.argv[1:]

config_file = script.parent / (script.stem + ".json")

# Default configuration
default_config = {
    "repo_api": "https://api.github.com/repos/FreeTubeApp/FreeTube/releases",
    "file_pattern": "^freetube_.*_amd64\\.AppImage$",
    "app_file":"FreeTube.AppImage",
    "latest_version": "",
    "get_releases":True,
    "get_prereleases":True
}

# Load configuration from file or use defaults
def load_config():
    if config_file.exists():
        with open(config_file) as f:
            config = json.load(f)
    else:
        config = default_config
        save_config(config)  # Save default config if file doesn't exist
    return config

# Save configuration to file
def save_config(config):
    with open(config_file, "w") as f:
        json.dump(config, f, indent=4)

# Function to download the latest release
def download_latest_release(download_url, file_name, latest_version):
    response = requests.get(download_url, stream=True)
    if response.status_code == 200:
        with open(file_name, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Download complete of: {file_name}")
        print(f"Updated to / downloaded version: {latest_version}")
    else:
        print("Failed to download the file.")

def runner(app):
    if app.exists():
        subprocess.run([str(app)] + args)
    else:
        print("There was some issue with the downloading, the app file\n'" + str(app) + "'\nis missing but should have been downloaded,\ncheck the config and submit a bug if the issue persists")

# Main script logic
def main():
    config = load_config()
    api_url = config.get("repo_api")
    app = script.parent / config.get("app_file")
    file_pattern = config.get("file_pattern")
    rel = config.get("get_releases", True)
    pre = config.get("get_prereleases", True)
    current_version = config.get("latest_version", "")

    # Get the release data from a github API / github compatible API
    response = requests.get(api_url)
    release_data = response.json()

    if not pre and not rel:
        rel = True

    data = []
    for item in release_data:
        if item.get('prerelease') and pre:
            data.append(item)
            break
        elif not item.get('prerelease') and rel:
            data.append(item)
            break


    latest_release = data[0]
    latest_version = latest_release["tag_name"]


    # Compare the current version with the latest version
    if current_version == latest_version:
        print(f"You already have the latest version ({current_version}) downloaded.")
        runner(app)
        return

    # Find the download URL for the desired asset
    download_url = next(
        (asset["browser_download_url"] for asset in latest_release["assets"]
         if re.match(file_pattern, asset["name"])),
        None
    )

    if not download_url:
        print(f"Download URL for {app.stem} not found in the latest release.")
        srunner(app)
        return

    # Download the file and update config with the new version
    download_latest_release(download_url, app, latest_version)
    config["latest_version"] = latest_version
    save_config(config)

    # Run the downloaded app
    runner(app)

if __name__ == "__main__":
    main()
