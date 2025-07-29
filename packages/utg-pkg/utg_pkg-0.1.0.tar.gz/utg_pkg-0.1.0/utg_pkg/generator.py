import os
import logging
from dotenv import load_dotenv
import google.generativeai as genai

# Prompt to generate tests
PROMPT = """
You are a senior Python developer.

Your task is to generate **comprehensive and production-ready unit tests** using the `pytest` framework for the following Python code.

Instructions:
1. **Cover all functions and class methods**, including edge cases and typical inputs.
2. Use **descriptive test names** that explain the scenario being tested.
3. If any function has external dependencies (e.g., file I/O, HTTP requests, database access), **mock them using pytest-mock or unittest.mock**.
4. **Group related tests** using classes or modules when appropriate.
5. Follow standard **pytest structure** (no need for `unittest.TestCase`).
6. Do not include the original code.
7. Avoid including `if __name__ == "__main__"` block.
8. Assume all necessary imports unless absolutely required to show.
9. The tests should be able to run **independently** of the original file structure.

Output only valid Python test code.
"""

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Load Gemini API key
load_dotenv(".env")
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise EnvironmentError("GEMINI_API_KEY not found in environment.")
genai.configure(api_key=api_key)

# Load model
model = genai.GenerativeModel("gemini-2.5-flash")

# Clean markdown code blocks from Gemini response
def clean_response(text: str) -> str:
    if text.startswith("```"):
        lines = text.strip().splitlines()
        if lines[0].startswith("```python"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        return "\n".join(lines)
    return text

# Get test code from Gemini
def get_response(prompt: str, code: str) -> str:
    logger.info("Sending prompt to Gemini...")
    try:
        response = model.generate_content(f"{prompt}\n\n```python\n{code}\n```")
        logger.info("Response received.")
        return clean_response(response.text)
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return "# ERROR: Gemini API failed to generate test code.\n"

# Recursively traverse project and generate tests
def traverse_and_generate_tests(src_root=".", test_root="tests"):
    logger.info(f"Starting test generation from source: {src_root}")
    for dirpath, _, filenames in os.walk(src_root):
        if test_root in dirpath or "__pycache__" in dirpath:
            continue  # Skip test and cache dirs

        for file in filenames:
            if file.endswith(".py") and not file.startswith("_"):
                src_file_path = os.path.join(dirpath, file)
                try:
                    with open(src_file_path, "r", encoding="utf-8-sig") as f:
                        code = f.read()
                    logger.info(f"Generating test for: {src_file_path}")
                    test_code = get_response(PROMPT, code)
                except Exception as e:
                    logger.warning(f"Failed to process {src_file_path}: {e}")
                    test_code = "# CONTENT NOT POSSIBLE"

                # Map to test path
                rel_path = os.path.relpath(src_file_path, src_root)
                test_path = os.path.join(test_root, rel_path).replace(".py", "_test.py")
                os.makedirs(os.path.dirname(test_path), exist_ok=True)

                # Write test file
                try:
                    with open(test_path, "w", encoding="utf-8") as out:
                        out.write(test_code)
                    logger.info(f"✅ Test written to: {test_path}")
                except Exception as e:
                    logger.error(f"Failed to write test file {test_path}: {e}")

if __name__ == "__main__":
    traverse_and_generate_tests()
