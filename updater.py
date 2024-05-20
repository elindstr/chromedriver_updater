import subprocess
import requests
import zipfile
import os
from typing import List, Dict, Optional

# Parameters
VERSION = ''
PACKAGE = 'chromedriver'
OS = 'windows'
PLATFORM = 'win64'
PATH = 'c:\\bin'
# OS = 'mac'
# PLATFORM = 'mac-x64'
# PATH = '/Users/elindstr/bin/chromedriver'

# Function to get local Chrome version
def get_local_chrome_version(os_type: str) -> str:
    if os_type == 'mac':
        command = '/Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --version'
        version = subprocess.check_output(command, shell=True).decode().split()[-1].strip()
    elif os_type == 'windows':
        command = 'reg query "HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon" /v version'
        version_info = subprocess.check_output(command, shell=True).decode()
        version = version_info.split()[-1].strip()
    elif os_type == 'linux':
        command = "google-chrome --version"
        version = subprocess.check_output(command, shell=True).decode().split()[-1].strip()
    else:
        raise ValueError("Unsupported OS type")
    print(f'Current local chrome version: {version}')
    return version

# Function to convert version string to tuple
def version_to_tuple(version: str) -> tuple:
    return tuple(map(int, version.split('.')))

# Function to find the closest version in JSON data
def find_closest_version(target_version: str, versions: List[Dict]) -> Dict:
    target_tuple = version_to_tuple(target_version)
    closest_match = None
    closest_diff = None

    for entry in versions['versions']:
        version_tuple = version_to_tuple(entry["version"])
        diff = tuple(abs(t - v) for t, v in zip(target_tuple, version_tuple))

        if closest_match is None or diff < closest_diff:
            closest_match = entry
            closest_diff = diff

    return closest_match

# Function to find the download URL based on package and platform
def find_download_url(closest_match: Dict, package: str, platform: str) -> Optional[str]:
    try:
        if package in closest_match['downloads']:
            for item in closest_match['downloads'][package]:
                if item['platform'] == platform:
                    return item['url']
    except KeyError as e:
        print(f"Key error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return None

# Function to extract file from zip archive
def extract_zip_file(zip_path: str, member_path: str, extract_to: str):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for member in zip_ref.namelist():
                if member_path in member:
                    zip_ref.extract(member, extract_to)
                    extracted_path = os.path.join(extract_to, member)
                    final_path = os.path.join(extract_to, os.path.basename(member))
                    if os.path.exists(final_path):
                        os.remove(final_path)
                    os.rename(extracted_path, final_path)
                    print(f'Extracted {member} to {final_path}')
                    break
    except zipfile.BadZipFile:
        print("Error: Bad zip file.")
    except Exception as e:
        print(f"An unexpected error occurred during extraction: {e}")

# Function to clean up downloaded and extracted files
def clean_up(zip_path: str, extracted_folder: str):
    try:
        if os.path.exists(zip_path):
            os.remove(zip_path)
            print(f'Removed zip file: {zip_path}')
        if os.path.exists(extracted_folder):
            os.rmdir(extracted_folder)
            print(f'Removed extracted folder: {extracted_folder}')
    except Exception as e:
        print(f"An unexpected error occurred during cleanup: {e}")

# Main execution
if __name__ == "__main__":
    # Get local Chrome version
    VERSION = get_local_chrome_version(OS)

    # Access JSON API endpoints
    url = 'https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json'
    response = requests.get(url)
    if response.status_code != 200:
        raise ConnectionError("Couldn't connect to chromedriver JSON endpoints page.")
    data = response.json()

    # Find closest version
    closest_match = find_closest_version(VERSION, data)
    print("Closest version available in JSON endpoints page:", closest_match['version'])

    # Locate driver download link
    download_url = find_download_url(closest_match, PACKAGE, PLATFORM)
    if not download_url:
        print(f"No matching downloads found for: Chrome version: {closest_match['version']}; package: {PACKAGE}; platform: {PLATFORM}.")
    else:
        try:
            # Download driver
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            zip_path = os.path.join(PATH, 'chromedriver.zip')
            with open(zip_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f'Successfully downloaded chromedriver to {zip_path}')

            # Extract the specific file from the downloaded zip file
            extract_zip_file(zip_path, f'{PACKAGE}-{PLATFORM}/chromedriver', PATH)

            # Clean up
            clean_up(zip_path, os.path.join(PATH, f'{PACKAGE}-{PLATFORM}'))

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
