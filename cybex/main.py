import logging

# from cybex.download import GitHubRepoDownloaderSingle
# from cybex.llm import OpenAI
import os
import shutil
import time
import zipfile
from zipfile import BadZipFile

import openai
import requests


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

class OpenAI:
    def __init__(
        self,
        api_key,
        strategy="cot",
        evaluation_strategy="value",
        api_base="",
        api_model="",
    ):
        if api_key == "" or api_key is None:
            api_key = os.environ.get("OPENAI_API_KEY", "")
        if api_key != "":
            openai.api_key = api_key
        else:
            raise Exception("Please provide OpenAI API key")

        if api_base == "" or api_base is None:
            api_base = os.environ.get("OPENAI_API_BASE", "")
        if api_base != "":
            openai.api_base = api_base
            print(f'Using custom api_base {api_base}')

        if api_model == "" or api_model is None:
            api_model = os.environ.get("OPENAI_API_MODEL", "")
        if api_model != "":
            self.api_model = api_model
        else:
            self.api_model = "text-davinci-003"
        print(f'Using api_model {self.api_model}')

        self.use_chat_api = 'gpt' in self.api_model
        self.strategy = strategy
        self.evaluation_strategy = evaluation_strategy

    def run(
        self,
        prompt,
        max_tokens,
        temperature,
        k=1,
        stop=None
    ):
        while True:
            try:
                if self.use_chat_api:
                    messages = [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                    response = openai.ChatCompletion.create(
                        model=self.api_model,
                        messages=messages,
                        max_tokens=max_tokens,
                        temperature=temperature,
                    )
                else:
                    response = openai.Completion.create(
                        engine=self.api_model,
                        prompt=prompt,
                        n=k,
                        max_tokens=max_tokens,
                        stop=stop,
                        temperature=temperature,
                    )
                with open("openai.logs", 'a') as log_file:
                    log_file.write("\n" + "-----------" + '\n' + "Prompt : " + prompt + "\n")
                return response
            except openai.error.RateLimitError as e:
                sleep_duration = os.environ.get("OPENAI_RATE_TIMEOUT", 30)
                print(f'{str(e)}, sleep for {sleep_duration}s, set it by env OPENAI_RATE_TIMEOUT')
                time.sleep(sleep_duration)

    def openai_choice2text_handler(self, choice):
        if self.use_chat_api:
            text = choice['message']['content']
        else:
            text = choice.text.strip()
        return text

    def generate_text(self, prompt, k):
        if self.use_chat_api:
            thoughts = []
            for _ in range(k):
                response = self.run(prompt, 400, 0.5, k)
                text = self.openai_choice2text_handler(response.choices[0])
                thoughts += [text]
            return thoughts
        else:
            response = self.run(prompt, 300, 0.5, k)
            thoughts = [self.openai_choice2text_handler(choice) for choice in response.choices]
            return thoughts


class TestGenerator:
    def __init__(
        self,
        repo_url,
        api_key,
        api_base="",
        api_model="gpt-4"
    ):
        self.repo_url = repo_url
        self.api_key = api_key
        self.api_base = api_base
        self.api_model = api_model
        self.openai_test_generator = OpenAI(
            api_key=self.api_key,
            api_base=self.api_base,
            api_model=self.api_model
        )
        logging.basicConfig(level=logging.INFO)

    def download(self):
        repo_name = self.repo_url.split('/')[-1]
        downloader = GitHubRepoDownloader(
            self.repo_url,
            repo_name
        )
        logging.info(f"Downloading repository: {self.repo_url}")
        downloader.download_repository()
        self.repo_path = os.path.join(os.getcwd(), repo_name)
    
    def generate_tests(self):
        logging.info("Generating tests...")
        python_files = self._find_python_files(self.repo_path, '.py')
        for python_file in python_files:
            self._generate_test_folder(python_file)
        logging.info("Tests generated successfully!")
    
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
            logging.info(f"Generating tests for {python_file}")
            test_content = self.openai_test_generator.generate_text(
                prompt,
                1
            )[0]
            test_file.write(test_content)

# Example usage:
test_generator = TestGenerator(
    repo_url="https://github.com/kyegomez/exa", 
    api_key=""
)
test_generator.download()
test_generator.generate_tests()