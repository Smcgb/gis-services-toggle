import os
import sys
from getpass import getpass
from pathlib import Path

from arcgis.gis.server import Server
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from dotenv import load_dotenv

MAX_WORKERS = 10  # Limit concurrent API requests to avoid overwhelming the server
ENV_FILE = Path(__file__).resolve().parent / ".env"


def load_config() -> tuple[str, str, str]:
    """
    Loads the ArcGIS Server URL and credentials from a .env file next to this script.

    Reads GIS_URL, GIS_USERNAME and GIS_PASSWORD. Real environment variables take
    precedence over values in the .env file. If GIS_USERNAME or GIS_PASSWORD is
    missing, the user is prompted for it (the password prompt does not echo).

    Returns:
        tuple[str, str, str]: (url, username, password)

    Raises:
        SystemExit: If GIS_URL is not set.
    """
    load_dotenv(ENV_FILE)

    url = os.getenv("GIS_URL", "").strip()
    if not url:
        sys.exit(f"GIS_URL is not set. Add it to {ENV_FILE} (see .env.example).")

    username = os.getenv("GIS_USERNAME", "").strip() or input("Please input the username\n")
    password = os.getenv("GIS_PASSWORD") or getpass("Please input the password for the user\n")
    return url, username, password

def connect_to_gis(url: str, username: str, password: str) -> Server:
    """
    Establishes a connection to a Standalone ArcGIS Server instance.

    This function attempts to authenticate with the provided server URL using the given 
    username and password. If the connection is successful, it returns a `Server` object 
    that can be used to interact with ArcGIS services and administrative endpoints. 
    If the connection fails, an error message is printed and the program exits.

    Args:
        url (str): The full URL of the ArcGIS Server (e.g., "https://example.com:6443/arcgis").
        username (str): The username for the ArcGIS Server account.
        password (str): The password for the ArcGIS Server account.

    Returns:
        Server: An authenticated `Server` object instance representing the ArcGIS Server.

    Raises:
        SystemExit: If the connection attempt fails and the function cannot authenticate.
    """

    try:
      server = Server(url=url, username=username, password=password)
      print("Successfully connected to the ArcGIS Server.")
      return server
    except Exception as e:
      print(f"Error connecting to the server: {e}")
      exit()

def get_services_folders(server: Server):
   
    """
    Retrieves and displays all service folder names from the connected ArcGIS Server.

    This function queries the provided `Server` object for all available service folders 
    (e.g., "Utilities", "System", "Hosted"). It prints the list of folders for user visibility 
    and returns them as a list of strings.

    Args:
        server (Server): An authenticated `Server` object connected to the ArcGIS Server instance.

    Returns:
        list[str]: A list of folder names available on the ArcGIS Server.

    Example:
        >>> server = connect_to_gis("https://example.com:6443/arcgis", "user", "pass")
        >>> folders = get_services_folders(server)
        Found services in these locations:
        System
        Utilities
        Hosted
        >>> print(folders)
        ['System', 'Utilities', 'Hosted']
    """ 
    services_folders = [service for service in server.services.folders]
    print("Found services in these locations:\n" + "\n".join(services_folders))
    return services_folders

def list_services(folder_name: str, server: Server):
    """
    Retrieves and displays all services within a specified folder on the ArcGIS Server.

    This function queries the connected ArcGIS Server for all services contained in the 
    given folder. It prints the total number of services found and returns a list of 
    service objects. If the folder name is empty or invalid, a message is displayed 
    and the function returns None.

    Args:
        folder_name (str): The name of the folder on the ArcGIS Server to list services from.
                           This value is case-sensitive. Use an empty string or None to 
                           represent the root folder.
        server (Server): An authenticated `Server` object connected to the ArcGIS Server instance.

    Returns:
        list: A list of `Service` objects within the specified folder if successful.
        None: If the folder name is invalid or an exception occurs.

    Example:
        >>> server = connect_to_gis("https://example.com:6443/arcgis", "user", "pass")
        >>> services = list_services("Utilities", server)
        Found 3 services in folder 'Utilities'.
        >>> for svc in services:
        ...     print(svc.properties.get("serviceName"))
        ParcelUpdate
        WaterMainMap
        CityBoundaries
    """

    if not folder_name:
        print(f"No services found in folder '{folder_name}'.")
        return
    else:
        try:
            hosted_folder = server.services.list(folder=folder_name)
            print(f"Found {len(hosted_folder)} services in folder '{folder_name}'.")
            for service in hosted_folder:
                print(service)
            return hosted_folder
        except Exception as e:
            print(f"Error listing services in folder '{folder_name}': {e}")
        return

def toggle_service(service, action: str):
    """Toggle a single service. Returns (success, message)."""
    service_name = service.properties.get('serviceName', str(service))
    print(f"{'Starting' if action == 'start' else 'Stopping'} service {service_name}")
    try:
        if action == 'start':
            service.start()
        else:
            service.stop()
        return (True, f"Successfully {'started' if action == 'start' else 'stopped'} service: {service_name}")
    except Exception as e:
        return (False, f"Error {'starting' if action == 'start' else 'stopping'} service {service_name}: {e}")


def collect_all_services(folders, server):
    """Fetch services from all folders in parallel."""
    all_services = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(list_services, folder, server): folder for folder in folders}
        for future in as_completed(futures):
            services = future.result()
            if services:
                all_services.extend(services)
    return all_services


def toggle_services_parallel(services, action: str):
    """Start or stop a list of services in parallel."""
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(toggle_service, service, action) for service in services]
        for future in as_completed(futures):
            success, message = future.result()
            print(message)


def main():
    print("You can use CTRL+C to stop this program at anytime. Please note that exiting before the program prompts you may have unintended consequences.")
    url, username, password = load_config()
    server = connect_to_gis(url, username, password)

    folders = get_services_folders(server)
    
    toggles = ['start', 'stop',]
    loop_program = True
    while loop_program:


        toggle_branch = input("Do you want to start or stop services? (input start or stop)\n")
        while toggle_branch.lower() not in toggles:
            toggle_branch = input("Do you want to start or stop services? (input start or stop)\n")

        # timeit
        

        if toggle_branch == 'stop':
            services_to_stop = input("Which services folder do you want to stop? Type All for all services. The services folders are Case Sensitive.\n")
            while services_to_stop not in folders and services_to_stop != 'All' :
                folders = get_services_folders(server)
                services_to_stop = input("Which services folder do you want to stop? Type All for all services. The services folders are Case Sensitive.\n")

            if services_to_stop == 'All':
                now = datetime.now()
                print(f'Stopping all services at {now}')
                all_services = collect_all_services(folders, server)
                toggle_services_parallel(all_services, 'stop')
                finish = datetime.now()
                print(f'finished at {finish}')
                print(f'Took {finish - now}')

            else:
                services = list_services(services_to_stop, server)
                choice = input(
                    "Press Enter to stop all services in this folder, "
                    "or input the full service link of the specific service you wish to stop: "
                    "You can copy the link from above by highlighting and right clicking in Powershell and use SHIFT+INSERT to paste.\n"
                    ).strip()
                
                if choice == '':
                    now = datetime.now()
                    print(f'Stopping folder services at {now}')
                    toggle_services_parallel(services, 'stop')
                    finish = datetime.now()
                    print(f'finished at {finish}')
                    print(f'Took {finish - now}')
                
                else:
                    now = datetime.now()
                    print(f'Stopping service {choice} at {now}')
    
                    try:
                       specific_service = server.get_service(choice)
                       specific_service.stop()
                       print(f"Successfully stopped service: {specific_service.properties.get('serviceName')}")
                    except Exception as e:
                       print(f"Error stopping service {choice}: {e}")

                    finish = datetime.now()
                    print(f'finished at {finish}')
                    print(f'Took {finish - now}')



        # starting services

        elif toggle_branch == 'start':
            services_to_start = input("Which services folder do you want to start? Type All for all services. The services folders are Case Sensitive.\n")
            while services_to_start not in folders and services_to_start != 'All' :
                folders = get_services_folders(server)
                services_to_start = input("Which services folder do you want to start? Type All for all services. The services folders are Case Sensitive.\n")

        # all services

            if services_to_start == 'All':
                now = datetime.now()
                print(f'Starting all services at {now}')
                all_services = collect_all_services(folders, server)
                toggle_services_parallel(all_services, 'start')
                finish = datetime.now()
                print(f'finished at {finish}')
                print(f'Took {finish - now}')

        # targetting a specific service

            else:
                services = list_services(services_to_start, server)
                choice = input(
                    "Press Enter to start all services in this folder, "
                    "or input the full service link of the specific service you wish to start: "
                    "You can copy the link from above by highlighting and right clicking in Powershell and use SHIFT+INSERT to paste.\n"
                    ).strip()

                if choice == "":
                    now = datetime.now()
                    print(f'Starting all folder services at {now}')
                    toggle_services_parallel(services, 'start')
                    finish = datetime.now()
                    print(f'finished at {finish}')
                    print(f'Took {finish - now}')

                else:
                    now = datetime.now()
                    print(f'Starting service {choice} at {now}')
                        
                    try:
                       specific_service = server.get_service(choice)
                       specific_service.start()
                       print(f"Successfully started service: {specific_service.properties.get('serviceName')}")
                    except Exception as e:
                       print(f"Error starting service {choice}: {e}")

                    finish = datetime.now()
                    print(f'finished at {finish}')
                    print(f'Took {finish - now}')

                    

        continue_program = input("Would you like to interact with another service? Input yes or no\n")
        while continue_program.lower() not in ['yes','no']:
            continue_program = input("Would you like to interact with another service? Input yes or no\n")
        if continue_program.lower() == 'no':
            loop_program = False

if __name__ == "__main__":
    main()