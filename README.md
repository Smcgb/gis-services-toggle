# ArcGIS Server Service Toggle Script
## Written by Shane Boyce 10-16-2025
**Developed for and made publicly available by the City of Corvallis Information Technology Department.**
### Overview

This script provides an interactive command-line utility to start or stop ArcGIS Server services in specific folders or across all folders on a Standalone ArcGIS Server instance.
It’s intended for administrative use and includes basic safeguards and dry-run functionality.

### How It Works
1. Loads the server URL and credentials from a `.env` file (prompts for username/password if they are not set).
2. Establishes a connection to the target server.
3. Retrieves and lists all available service folders.
4. Asks whether to start or stop services.
5. Executes the selected action for either a single folder or all folders.
6. Prints out actions 

### Requirements
- Python 3.10<=3.12
- ArcGIS API for Python (arcgis)
- Network access to the ArcGIS Server instance

Install dependencies:
```bash
uv sync
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
Please input the username: admin
Please input the password for the user:
Successfully connected to the ArcGIS Server.
Found services in these locations:
System
Utilities
Hosted
Do you want to start or stop services? (input start or stop): stop
Which services folder do you want to stop? Type All for all services. The services folders are Case Sensitive: All
Stopping all services...
Stopping service MapServer1
Stopping service MapServer2
```

### Notes
- Exiting with CTRL+C mid-operation may leave services in an inconsistent state.
- Folder names are case-sensitive and must match exactly.
- For unattended runs, set all three values in `.env` or as environment variables.
- Modify the script to uncomment the service.start() and service.stop() lines once you have verified behavior.

### Acknowledgements
This script was developed by Shane Boyce for the City of Corvallis Information Technology Department and is shared publicly with their permission.