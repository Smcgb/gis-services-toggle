# ArcGIS Server Service Toggle Script
## Written by Shane Boyce 10-16-2025
**Developed for and made publicly available by the City of Corvallis Information Technology Department.**
### Overview

This script provides an interactive command-line utility to start or stop ArcGIS Server services in specific folders or across all folders on a Standalone ArcGIS Server instance.
It’s intended for administrative use. Services are started or stopped in parallel, and the script validates your input before taking any action.

### How It Works
1. Loads the server URL and credentials from a `.env` file (prompts for username/password if they are not set).
2. Establishes a connection to the target server.
3. Retrieves and lists all available service folders.
4. Asks whether to start or stop services.
5. Executes the selected action for either a single folder or all folders.
6. Prints the result of each action and how long the run took.

### Requirements
- Python 3.10–3.12
- [uv](https://docs.astral.sh/uv/) for installing dependencies and running the script
- Network access to a Standalone ArcGIS Server instance and an administrator account on it

Dependencies (including the ArcGIS API for Python, `arcgis`) are listed in `pyproject.toml`.

### Getting Started
```bash
git clone https://github.com/Smcgb/gis-services-toggle.git
cd gis-services-toggle
cp .env.example .env    # then edit .env (see Configuration below)
uv sync
uv run gis-service-toggle.py
```

### Configuration
Copy `.env.example` to `.env` next to the script and fill it in:
```
GIS_URL=https://your-server.example.com:6443/arcgis
GIS_USERNAME=admin
GIS_PASSWORD=
```
- `GIS_URL` is required.
- `GIS_USERNAME` / `GIS_PASSWORD` are optional; if left blank you'll be prompted (the password prompt is hidden).
- Real environment variables override values in `.env`.
- `.env` is git-ignored. Restrict its permissions if you store the password in it (e.g. `chmod 600 .env`).

Example interaction:
```
You can use CTRL+C to stop this program at anytime...
Successfully connected to the ArcGIS Server.
Found services in these locations:
System
Utilities
Hosted
Do you want to start or stop services? (input start or stop): stop
Which services folder do you want to stop? Type All for all services. The services folders are Case Sensitive: All
Stopping all services at 2025-10-16 14:02:11.482913
Stopping service MapServer1
Stopping service MapServer2
Successfully stopped service: MapServer1
Successfully stopped service: MapServer2
finished at 2025-10-16 14:02:19.105377
Took 0:00:07.622464
Would you like to interact with another service? Input yes or no
```

### Notes
- Exiting with CTRL+C mid-operation may leave services in an inconsistent state.
- Folder names are case-sensitive and must match exactly.
- If `GIS_USERNAME` and `GIS_PASSWORD` are set, the script skips the login prompts. Choosing which services to start or stop is always interactive.
- The script really starts and stops services. There is no dry-run mode, so double-check the folder you choose.

### Acknowledgements
This script was developed by Shane Boyce for the City of Corvallis Information Technology Department and is shared publicly with their permission.

### AI Disclosure
AI assistance (Claude) was used for two limited changes: moving the hardcoded server URL and interactive username/password entry to `.env`-based configuration, and a final bug-fix sweep. All other code is original work by Shane Boyce.

The commits containing these AI-assisted changes, including the initial commit of this repository, are marked as co-authored by Claude.

### Repository History
This repository was created from an export of the code. The project was originally developed in a different git hosting environment, and its previous commit history was not carried over, so it is unavailable here.
