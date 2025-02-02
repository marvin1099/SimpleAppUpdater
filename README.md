# SimpleAppUpdater

**SimpleAppUpdater** is a versatile Python-based script that automates the process of checking for, downloading, and launching the latest version of an application from a GitHub repository or similar API. It is designed to update any portable application that follows a GitHub-like API structure with a list of releases, each containing `tag_name` and a `browser_download_url` in the assets section.

## Features

- **General-Purpose Updater**: Works with any portable app compatible with GitHub-style release APIs.
- **Configurable**: Customizable via a JSON config file based on the script’s name, allowing for multiple app updaters.
- **Supports Binary Execution**: Can be compiled to a standalone binary, and configuration will work seamlessly with both compiled and script versions.

## Requirements

- Python 3.x
- `requests` library for HTTP requests

Install the required package using:
```
pip install requests
```

## Usage

### Downloading
Check out the [releases section](https://codeberg.org/marvin1099/https://codeberg.org/marvin1099/SimpleAppUpdater/releases) for the latest py file.
Binarys will be added in soon.

### Running the Script

To check for updates and run the app, execute:
```
app_updater.py
```

When run, the script:
1. Loads its configuration from a JSON file named after the script (`app_updater.json` in this case).
2. If the file is missing it gets created and the app exits so the file can be edited.
3. Checks the API for the latest release or pre-release version based on the config.
4. Downloads the latest version if it’s newer than the current version stored in the config.
5. Launches the application with any arguments provided.

### Command-Line Arguments

Any arguments passed to `app_updater.py` will be forwarded to the application after it has updated and started.

### Config File (`app_updater.json`)

A configuration file with the same name as the script (ending with `.json`)  
will be created automatically, storing settings for the updater.
But as mentioned if the configuration file is created the fist time the app will exit,   
to allow editing of the config before running the updater.

#### Example Configuration
This is also the default config, here provided as an example. 

```
{
    "repo_api": "https://api.github.com/repos/FreeTubeApp/FreeTube/releases",
    "file_pattern": "freetube-([0-9.]+)-amd64\\.AppImage",
    "app_file": "FreeTube.AppImage",
    "latest_version": "",
    "get_releases": true,
    "get_prereleases": true
}
```

#### Configuration Options

- `repo_api`: URL of the API providing the releases. This API should return a list of releases, each containing a `tag_name` for versioning and a `browser_download_url` in the `assets` section.
- `file_pattern`: Regex pattern to match the name of the downloadable asset.
- `app_file`: Filename to save and launch the downloaded application.
- `latest_version`: Tracks the last downloaded version of the application.
- `get_releases`: Set to `true` to include releases in update checks.
- `get_prereleases`: Set to `true` to include pre-releases in update checks.

If get_releases and get_prereleases are false get_releases will be set to true.
This is like that, so there is allways something to download.

### Example Workflow

1. **Check for Updates**: The script queries the API for release data and selects the latest version based on `tag_name`.
2. **Compare Versions**: It compares the latest version with the version recorded in the config file.
3. **Download and Run**: If a new version is available, it downloads the asset, updates `latest_version` in the config, and then launches the app.

### Multiple Updaters

Each instance of this updater script can be renamed for a specific application, and it will create a unique config file (`vlc_updater.json` if named `vlc_updater.py`, `freetube_updater.json` if named `freetube_updater.py`, etc.). This makes it easy to manage multiple apps using this same updater.