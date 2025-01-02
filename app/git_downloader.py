import os
import json
import requests
import zipfile
from tqdm import tqdm

from app.utils.style import Colors

class GitDownloader:
    def __init__(self):
        """
        Initializes the GitDownloader class.
        Sets up necessary paths for caching and storing ETag information.
        Creates the cache directory if it doesn't already exist.
        """

        current_dir = os.path.dirname(os.path.abspath(__file__))

        self.app_dir = os.path.join(current_dir, 'cache')
        self.etag_file = os.path.join(self.app_dir, 'etag.json')
        self.zip_path = os.path.join(self.app_dir, 'cache.zip')

        # Create cache folder if it doesn't exist
        if not os.path.exists(self.app_dir):
            os.makedirs(self.app_dir)

    def get_etag(self):
        """
        Retrieves the saved ETag for the current URL from the etag.json file, if it exists.

        Returns:
        str or None: The ETag value if available, otherwise None.
        """
        if os.path.exists(self.etag_file):
            with open(self.etag_file, 'r') as f:
                etag_data = json.load(f)
                return etag_data.get(self.url)
        return None

    def save_etag(self, etag):
        """
        Saves the new ETag for the current URL to etag.json.
        
        Args:
        etag (str): The new ETag value to be saved.
        """
        etag_data = {}
        if os.path.exists(self.etag_file):
            with open(self.etag_file, 'r') as f:
                etag_data = json.load(f)

        etag_data[self.url] = etag

        with open(self.etag_file, 'w') as f:
            json.dump(etag_data, f, indent=4)

    def extract_specific_folder(self, zip_path, target_folder, extract_to):
        """
        Extracts only the specified folder from a ZIP archive.

        Args:
        zip_path (str): Path to the ZIP file.
        target_folder (str): The folder inside the ZIP file to be extracted.
        extract_to (str): The path to the directory where the files will be extracted.
        """
        with zipfile.ZipFile(zip_path, 'r') as z:
            for file_info in z.infolist():
                # Check if the file is inside the target folder
                if file_info.filename.startswith(target_folder):
                    # Determine extraction path
                    extract_path = os.path.join(extract_to, file_info.filename)
                    
                    if file_info.is_dir():
                        os.makedirs(extract_path, exist_ok=True)
                    else:
                        with open(extract_path, 'wb') as f:
                            f.write(z.read(file_info.filename))

    def download_and_extract(self, url, name='', target_folder=''):
        """
        Main function to download and extract the ZIP file if changes are detected based on the ETag.
        
        Args:
        url (str): The URL to download the ZIP file from.
        name (str): A friendly name for the download, used in the status messages.
        target_folder (str): The folder inside the ZIP file to extract.
        
        The function checks if the remote content has changed by comparing the ETag. 
        If changes are detected, it downloads and extracts the specified folder from the ZIP file.
        """
        self.url = url
        etag = self.get_etag()

        # Add ETag to headers if available
        headers = {}
        if etag:
            headers['If-None-Match'] = etag

        # Send request to check for updates
        response = requests.get(self.url, headers=headers, stream=True)

        if response.status_code == 304:
            # No updates, skipping download
            print(f"No updates {Colors.text(name)} found. Skipping download.")
            return
        elif response.status_code == 200:
            # Update found, proceed with download
            print(f"Updates {Colors.text(name)} found. Downloading new file...")

            # Total size of the file for progress bar
            total_size = int(response.headers.get('content-length', 0))

            # Download the file with progress bar
            with open(self.zip_path, 'wb') as f:
                for data in tqdm(response.iter_content(1024), total=total_size // 1024, unit='KB'):
                    f.write(data)

            # Extract the specific folder from the ZIP
            self.extract_specific_folder(self.zip_path, target_folder, self.app_dir)

            # Remove the ZIP file after extraction is done
            os.remove(self.zip_path)

            # Save the new ETag
            new_etag = response.headers.get('ETag')
            if new_etag:
                self.save_etag(new_etag)

            print(f"Download and extraction {Colors.text(name)} completed. Files extracted to {self.app_dir}, and the ZIP file has been removed.")
        
        else:
            # Error handling if request fails
            print(f"Error: Unable to download {name}. HTTP Status Code: {response.status_code}")
