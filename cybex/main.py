import os

class TestGenerator:
    def __init__(self, repo_path, exclude_extension=".py"):
        self.repo_path = repo_path
        self.exclude_extension = exclude_extension

    def generate_tests(self):
        python_files = self._find_python_files(self.repo_path, self.exclude_extension)
        for python_file in python_files:
            self._generate_test_folder(python_file)

    def _find_python_files(self, directory, extension):
        python_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(extension):
                    python_files.append(os.path.join(root, file))
        return python_files

    def _generate_test_folder(self, python_file):
        test_folder = os.path.dirname(python_file).replace("src", "test")
        test_file = python_file.replace("src", "test")

        os.makedirs(test_folder, exist_ok=True)
        with open(test_file, "w") as test_file:
            test_file.write(f"# Tests for {python_file}\n\n")

# Example usage:
test_generator = TestGenerator(repo_path="path_to_repo", exclude_extension=".py")
test_generator.generate_tests()
