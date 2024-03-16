import subprocess, requests

# Parameters
VERSION = ''
PACKAGE = 'chromedriver'
OS = 'mac'
PLATFORM = 'mac-x64'
PATH = '/Users/elindstr/bin/chromedriver'
# OS = 'windows'
# PLATFORM = 'win64'
# PATH = 'c:\\bin'

# Get local chrome version (mac)
command = '/Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --version'
VERSION = subprocess.check_output(command, shell=True).decode()
VERSION = VERSION.split()[-1].strip() 
print(f'Current local chrome version (full): {VERSION}')

VERSIONtop = VERSION.split('.')[0]
print(f'Current local chrome version (top-level): {VERSIONtop}')

## Get local chrome version (windows)
# command = 'reg query "HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon" /v version'
# version_info = subprocess.check_output(command, shell=True).decode()
# VERSION = version_info.split()[-1]

## Get local chrome version (linux)
# command = "google-chrome --version"
# VERSION = subprocess.check_output(command, shell=True).decode()

# Access JSON API endpoints
url = 'https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json'
response = requests.get(url)
if response.status_code != 200:
    print("Couldn't connect to chromedriver JSON endpoints page.")
data = response.json()

# Locate driver download link based on parameters
download_url = ""
for version in reversed(data['versions']):
    if VERSIONtop in version['version'].split('.')[0]:
        if PACKAGE in version['downloads']:
            for download in reversed(version['downloads'][PACKAGE]):
                if download['platform'] == PLATFORM:
                    download_url = download['url']
                    break
    if download_url:
        break

# Download driver to PATH
if not download_url:
    print(f"No matching chromedriver found for Chrome version {VERSIONtop}.")
else:
    response = requests.get(download_url, stream=True)
    response.raise_for_status()
    with open(PATH, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
    print(f'Updated chromedriver to {VERSIONtop}.')


    