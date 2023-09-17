import os
import requests
import zipfile
from zipfile import BadZipFile
import shutil

class GitHubRepoDownloaderSingle:
    """
    A utility class to download and unzip a single GitHub repository and remove code files of a certain extension.

    Args:
        username (str): GitHub username.
        repo_name (str): Name of the GitHub repository.
        download_dir (str): Directory to store the downloaded repository.
        exclude_extension (str): File extension to exclude (default is '.py').

    Attributes:
        username (str): GitHub username.
        repo_name (str): Name of the GitHub repository.
        download_dir (str): Directory to store the downloaded repository.
        exclude_extension (str): File extension to exclude.

    Example:
        downloader = GitHubRepoDownloaderSingle(username="lucidrains", repo_name="repo-name",
                                                download_dir="lucidrains_repo", exclude_extension=".py")
        downloader.download_repository()
    """

    def __init__(self, username, repo_name, download_dir, exclude_extension=".py"):
        self.username = username
        self.repo_name = repo_name
        self.api_url = f"https://api.github.com/repos/{username}/{repo_name}/zipball/master"
        self.download_dir = download_dir
        self.exclude_extension = exclude_extension
        os.makedirs(self.download_dir, exist_ok=True)

    def download_repository(self):
        """
        Downloads and unzips a single GitHub repository.

        Raises:
            RuntimeError: If there is an error during download or unzip.
        """
        zip_file_path = os.path.join(self.download_dir, f"{self.repo_name}.zip")
        zip_response = requests.get(self.api_url)
        if zip_response.status_code == 200:
            with open(zip_file_path, "wb") as zip_file:
                zip_file.write(zip_response.content)
            try:
                self._unzip_repository(zip_file_path)
                print(f"Downloaded and unzipped {self.repo_name}")
                self._remove_files_by_extension(self.download_dir, self.exclude_extension)
                print(f"Removed files with extension {self.exclude_extension}")
            except BadZipFile:
                print(f"Invalid ZIP file for {self.repo_name}")
        else:
            raise RuntimeError(f"Failed to download {self.repo_name}")
        print(f"{self.repo_name} downloaded, unzipped, and cleaned.")

    def _unzip_repository(self, zip_file_path):
        """
        Unzips a repository ZIP file.

        Args:
            zip_file_path (str): Path to the ZIP file to unzip.

        Raises:
            BadZipFile: If the ZIP file is invalid.
        """
        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            zip_ref.extractall(self.download_dir)

    def _remove_files_by_extension(self, directory, extension):
        """
        Removes files with a specific extension from a directory.

        Args:
            directory (str): Directory to remove files from.
            extension (str): File extension to exclude.
        """
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(extension):
                    os.remove(os.path.join(root, file))

# Example usage:
downloader = GitHubRepoDownloaderSingle(username="lucidrains", repo_name="repo-name",
                                       download_dir="lucidrains_repo", exclude_extension=".py")
try:
    downloader.download_repository()
except RuntimeError as e:
    print(f"Error: {e}")