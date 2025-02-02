#!/usr/bin/env python

import re
import os
import sys
import json
import requests
import platform
import subprocess
from pathlib import Path

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
    "file_pattern": "freetube-([0-9.]+)-amd64\\.AppImage",
    "app_file":"FreeTube.AppImage",
    "latest_version": "",
    "get_releases":True,
    "get_prereleases":True
}

if platform.system() == "Linux":
    if "SatisfactoryModManager".lower() in str(script.name).lower():
        default_config.update({
            "repo_api": "https://api.github.com/repos/satisfactorymodding/SatisfactoryModManager/releases",
            "file_pattern": "SatisfactoryModManager_linux_amd64",
            "app_file":"SatisfactoryModManager"
        })
    elif "Suyu".lower() in str(script.name).lower():
        default_config.update({
            "repo_api": "https://git.suyu.dev/api/v1/repos/suyu/suyu/releases",
            "file_pattern": "Suyu-Linux_x86_64\\.AppImage",
            "app_file":"Suyu.AppImage"
        })
elif platform.system() == "Windows":
    default_config.update({
        "file_pattern": "freetube-([0-9.]+)-win-x64-portable\\.exe",
        "app_file":"FreeTube.exe"
    })

# Load configuration from file or use defaults
def load_config():
    if config_file.exists():
        with open(config_file) as f:
            config = json.load(f)
    else:
        config = default_config
        save_config(config)
        print("Config was created. Exiting to allow config editing")
        exit()

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
        print(f"Download complete of: \"{download_url}\"")
        print(f"The file was saved as: \"{file_name}\"")
        print(f"Updated to / downloaded version: \"{latest_version}\"")
    else:
        print("Failed to download the file.")

def runner(app):
    if app.exists():
        config = load_config()
        if config.get("missing_file"):
            del config["missing_file"]
            save_config(config)
            del config

        print(f"\n--- Starting {app.name} ---\n")
        subprocess.run([str(app)] + args)
        return
    else:
        config = load_config()
        missing_file = config.get("missing_file", False)
        latest_version = config.get("latest_version")
        if not latest_version:
            print("App was not jet downloaded. Closing")
            return
        if not missing_file:
            config["missing_file"] = True
            config["latest_version"] = ""
            save_config(config)
            print(f"The file {app.name} is missing, tying to redownload\n")
            main()
            config = load_config()
            if not config.get("latest_version"):
                config["latest_version"] = latest_version
            save_config(config)
            return
        else:
            del config["missing_file"]
            save_config(config)

        print(f"\nThere was some issue with the downloading, the app file\n\t'{app}'\nis missing but should have been downloaded,\ncheck the config and submit a bug if the issue persists")
        return

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
    if response.status_code == 404:
        print("URL not found.\nStarting last downloaded app.")
        runner(app)
        return
    elif response.status_code >= 500 and response.status_code < 600:
        print("Server error: {} {}".format(response.status_code, response.reason))
        runner(app)
        return
    else:
        if response.content.strip() == b'':
            print("Response is empty or contains no data.\nStarting last downloaded app.")
            runner(app)
            return
    try:
        release_data = response.json()
    except Exception as e:
        print("Did not get any json data from the response.\nStarting last downloaded app.")
        runner(app)
        return


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

    try:
        latest_release = data[0]
        latest_version = latest_release["tag_name"]
    except Exception as e:
        print("Was not able to get the data or the release tag.\nStarting last downloaded app.")
        runner(app)
        return

    # Compare the current version with the latest version
    if current_version == latest_version:
        print(f"You already have the latest version ({current_version}) downloaded.\nStarting last downloaded app.")
        runner(app)
        return

    # Find the download URL for the desired asset
    download_url = next(
        (asset["browser_download_url"] for asset in latest_release["assets"]
         if re.match(file_pattern, asset["name"])),
        None
    )

    if not download_url:
        print(f"Download URL for {app.stem} not found in the latest release.\nFile assets or the file regex where not found.\nStarting last downloaded app.")
        runner(app)
        return

    # Download the file and update config with the new version
    download_latest_release(download_url, app, latest_version)
    config["latest_version"] = latest_version
    save_config(config)

    # Run the downloaded app
    runner(app)

if __name__ == "__main__":
    main()
