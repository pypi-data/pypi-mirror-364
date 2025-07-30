#!/usr/bin/env python3
import os
import sys
import glob
import requests
import json
import pytest

API_KEY = os.getenv('ANTHROPIC_API_KEY')
CLAUDE_API_URL = 'https://api.anthropic.com/v1/messages'

if not API_KEY:
    print('Error: ANTHROPIC_API_KEY environment variable not set.')
    sys.exit(1)

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

PYTHONPATH_FIX = (
    "import sys\n"
    "import os\n"
    "sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))\n"
)

def get_python_files(app_path):
    return [y for x in os.walk(app_path) for y in glob.glob(os.path.join(x[0], '*.py'))]

def read_files(file_paths):
    code = ''
    for path in file_paths:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            code += f'\n# File: {path}\n' + f.read() + '\n'
    return code

def generate_test_cases(code):
    headers = {
        'x-api-key': API_KEY,
        'anthropic-version': '2023-06-01',
        'content-type': 'application/json',
    }
    prompt = (
        "You are an expert Python developer and QA engineer. "
        "Given the following Python application code, write comprehensive unit tests for it. "
        "Use pytest style. Output only the test code, no explanations. "
        "If the code is too large, focus on the most important functions/classes.\n"
        f"\n{code}\n"
    )
    data = {
        "model": "claude-3-5-sonnet-20241022",  # You can change to another Claude model if needed
        "max_tokens": 2048,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(CLAUDE_API_URL, headers=headers, data=json.dumps(data))
    if response.status_code != 200:
        print('Error from Claude API:', response.status_code, response.text)
        sys.exit(1)
    result = response.json()
    # Claude's response format may vary; adjust as needed
    return result.get('content', result)

def clean_test_code(test_code):
    # Remove triple backticks and ```python from start/end
    lines = test_code.strip().splitlines()
    # Remove leading code block markers
    while lines and (lines[0].strip() == '```' or lines[0].strip() == '```python'):
        lines.pop(0)
    # Remove trailing code block markers
    while lines and lines[-1].strip() == '```':
        lines.pop()
    return '\n'.join(lines).strip()

def write_test_files(app_path, py_files, test_cases):
    tests_dir = os.path.join(app_path, 'tests')
    os.makedirs(tests_dir, exist_ok=True)
    if isinstance(test_cases, list):
        test_texts = [obj.get('text', '') for obj in test_cases]
    elif isinstance(test_cases, str):
        test_texts = [test_cases]
    else:
        test_texts = [str(test_cases)]
    # Clean up code blocks
    test_texts = [clean_test_code(tc) for tc in test_texts]
    if len(py_files) == len(test_texts):
        for src, test_code in zip(py_files, test_texts):
            src_name = os.path.basename(src)
            test_file = os.path.join(tests_dir, f'test_{src_name}')
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(PYTHONPATH_FIX + test_code + '\n')
    else:
        test_file = os.path.join(tests_dir, 'test_generated.py')
        with open(test_file, 'w', encoding='utf-8') as f:
            for test_code in test_texts:
                f.write(PYTHONPATH_FIX + test_code + '\n')

@pytest.fixture
def temp_tasks_file(tmp_path, monkeypatch):
    temp_file = tmp_path / "tasks.json"
    # Patch the path in your app to use this temp file
    monkeypatch.setattr("notes_app.storage.TASKS_FILE", str(temp_file))
    return str(temp_file)

def main():
    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} /path/to/python/app')
        sys.exit(1)
    app_path = sys.argv[1]
    if not os.path.isdir(app_path):
        print(f'Error: {app_path} is not a directory')
        sys.exit(1)
    py_files = get_python_files(app_path)
    if not py_files:
        print('No Python files found in the specified directory.')
        sys.exit(1)
    code = read_files(py_files)
    print('Generating test cases using Claude...')
    test_cases = generate_test_cases(code)
    print('Writing test cases to tests/ directory...')
    write_test_files(app_path, py_files, test_cases)
    print('Test cases written to tests/ directory.')

if __name__ == '__main__':
    main() 