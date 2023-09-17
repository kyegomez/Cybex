
import os
import requests
import zipfile
from zipfile import BadZipFile
import shutil

class GitHubRepoDownloader:
    """
    A utility class to download and unzip a single GitHub repository.
    """
    def __init__(self, repo_url, download_dir):
        self.repo_url = repo_url
        self.download_dir = download_dir
        os.makedirs(self.download_dir, exist_ok=True)

    def download_repository(self):
        repo_name = self.repo_url.split('/')[-1]
        zip_url = f"{self.repo_url}/archive/refs/heads/master.zip"
        zip_file_path = os.path.join(self.download_dir, f"{repo_name}.zip")
        zip_response = requests.get(zip_url)
        if zip_response.status_code == 200:
            with open(zip_file_path, "wb") as zip_file:
                zip_file.write(zip_response.content)
            try:
                self._unzip_repository(zip_file_path)
                os.remove(zip_file_path)
                print(f"Downloaded and unzipped {repo_name}")
            except BadZipFile:
                print(f"Invalid ZIP file for {repo_name}")
        else:
            print(f"Failed to download {repo_name}")

    def _unzip_repository(self, zip_file_path):
        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            zip_ref.extractall(self.download_dir)

# Example usage:
downloader = GitHubRepoDownloader(
    repo_url="https://github.com/kyegomez/repo-name", 
    download_dir="repository"
)
downloader.download_repository()