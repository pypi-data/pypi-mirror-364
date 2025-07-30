# TestCases Writer AI Tool

Automatically generate comprehensive pytest test cases for your Python application using Claude AI.

## Features

- Scans your Python project and sends code to Claude AI to generate high-quality pytest test cases.
- Writes the generated tests to a `tests/` directory in your project.
- Ensures test files are import-safe by patching `sys.path`.
- Supports file-based storage patching for isolated tests (see advanced usage).

---

## Requirements

- Python 3.7+
- [Anthropic Claude API key](https://docs.anthropic.com/claude/docs/quickstart)
- Internet connection (for API calls)
- Packages in `requirements.txt` (install with `pip install -r requirements.txt`)

---

## Installation

1. **Clone this repository** (or copy the tool files):

   ```bash
   git clone <your-repo-url>
   cd TestCases_Writer_AI_Tool
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set your Anthropic API key:**

   ```bash
   export ANTHROPIC_API_KEY=sk-ant-...
   ```

---

## Usage

1. **Run the tool on your Python app:**

   ```bash
   python generate_test_cases.py /path/to/your/python/app
   ```

   - Replace `/path/to/your/python/app` with the path to the root of your Python project.
   - The tool will scan all `.py` files, send them to Claude, and write generated tests to a `tests/` directory inside your app.

2. **Run the generated tests:**

   ```bash
   cd /path/to/your/python/app
   pytest
   ```

---

## How It Works

- The tool collects all Python files in your app.
- It sends the code to Claude AI with a prompt to generate pytest-style tests.
- The generated tests are written to `tests/test_generated.py` (or one test file per source file).
- Each test file includes a snippet to patch `sys.path` for import safety.

---

## Advanced: Isolating File-Based Storage in Tests

If your app uses a file (like `tasks.json`) for storage, the tool can generate a pytest fixture to patch the storage path using `tmp_path` and `monkeypatch`. This ensures each test runs in isolation and avoids data leakage between tests.

Example fixture (auto-included if detected):

```python
import pytest

@pytest.fixture
def temp_tasks_file(tmp_path, monkeypatch):
    temp_file = tmp_path / "tasks.json"
    monkeypatch.setattr("notes_app.storage.TASKS_FILE", str(temp_file))
    return str(temp_file)
```

---

## Troubleshooting

- **ModuleNotFoundError:**  
  Make sure you run `pytest` from your project root, and that the generated test files include the `sys.path` patch at the top.
- **API Errors:**  
  Ensure your `ANTHROPIC_API_KEY` is set and valid.
- **No tests generated:**  
  Check that your app directory contains `.py` files and is accessible.

---

## License

MIT License

---

## Credits

- Built with [Anthropic Claude API](https://www.anthropic.com/).
- Test generation logic by [your name or org]. 