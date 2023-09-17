import os
import requests
import zipfile
import time
import openai
from zipfile import BadZipFile
from cybex.llm import OpenAI
from cybex.download import GitHubRepoDownloaderSingle

class TestGenerator:
    def __init__(
        self,
        repo,
        api_key,
        api_base="",
        api_model=""
    ):
        self.repo = repo
        self.api_key = api_key
        self.api_base = api_base

        self.api_model = api_model
        self.openai_test_generator = OpenAI(
            api_key=self.api_key,
            api_base=self.api_base,
            api_model=self.api_model
        )

    def download(self):
        username, repo_name = self.repo.split('/')[-2]
        downloader = GitHubRepoDownloaderSingle(
            username,
            repo_name,
            repo_name
        )
        downloader.download_repository()
        self.repo_path = os.path.join(os.getcwd(), repo_name)
    
    def generate_tests(self):
        python_files = self._find_python_files(self.repo_path, '.py')
        for python_file in python_files:
            self._generate_test_folder(python_file)
    
    def _find_python_files(
        self,
        directory,
        extension
    ):
        python_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(extension):
                    python_files.append(os.path.join(root, file))
        return python_files
    
    def _generate_test_folder(
        self,
        python_file
    ):
        test_folder = os.path.dirname(python_file).replace('src', 'test')
        test_file = python_file.replace('src', 'test')

        os.makedirs(test_folder, exist_ok=True)
        with open(test_file, "w") as test_file:
            test_file.write(f"# Tests for {python_file}\n\n")
            with open(python_file, 'r') as code_file:
                code_content = code_file.read()
            prompt = f"""
            Given the following code:
            {code_content}

            Please generate comprehensive unit tests that cover all functions and edge cases. 
            The tests should use the pytest framework and follow best practices for test design, 
            including clear assertion messages and appropriate use of setup, teardown, 
            and fixture functions where necessary. DO NOT RESPOND WITH ANYTHING OTHER THAN PYTORCH CODE
            """
            test_content = self.openai_test_generator.generate_text(
                prompt,
                1
            )[0]
            test_file.write(test_content)