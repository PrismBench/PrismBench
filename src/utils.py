import ast
import re
import subprocess
from typing import Dict, List, Optional, Tuple

from loguru import logger


def extract_content_from_text(
    text: str,
    start_delimiter: str,
    end_delimiter: str,
) -> Optional[str]:
    """
    Extract content from text between start and end delimiters.

    Args:
        text (str): the text to extract content from. folows the pattern <start_delimiter>content<end_delimiter>
        start_delimiter (str): the start delimiter.
        end_delimiter (str): the end delimiter.

    Returns:
        Optional[str]: the text content between the start and end delimiters.
    """
    logger.debug(
        f"Extracting content between '{start_delimiter}' and '{end_delimiter}'"
    )

    pattern = f"{re.escape(start_delimiter)}(.*?){re.escape(end_delimiter)}"
    match = re.search(pattern, text, re.DOTALL)

    return match.group(1).strip() if match else None


def check_syntax(code: str) -> bool:
    """
    Check the syntax of the code.

    Args:
        code (str): the code to check.

    Returns:
        bool: True if the code is valid, False otherwise.
    """
    try:
        ast.parse(code)
        logger.debug("Syntax check passed.")
        return True
    except SyntaxError:
        logger.debug("Syntax check failed.")
        return False


def extract_code_blocks(text: str) -> Dict[str, List[Tuple[str, str]]]:
    """
    Extracts code blocks of specified types from the given text.

    Args:
        text (str): The text to extract code from.
    Returns:
        List[Tuple[str, str]]: A list of tuples containing the block name and its body.
    """
    # First, check for code blocks with triple backticks
    patterns = {
        "class": r"class\s+(\w+)[^\n]*:",
        "function": r"def\s+(\w+)[^\n]*:",
        "test": r"def\s+(test_\w+)[^\n]*:",
    }

    blocks = {k: [] for k in patterns.keys()}

    for block_type in patterns.keys():
        matches = re.finditer(patterns[block_type], text)
        for match in matches:
            name = match.group(1)
            start = match.start()
            end = find_block_end(text, start)
            blocks[block_type].append((name, text[start:end].strip()))

    return blocks


def find_block_end(text: str, start: int) -> int:
    """
    Find the end of a code block starting from a given position.
    A block ends when the indentation level decreases or a new block starts.

    Args:
        text: The text to search.
        start: The starting position of the block.

    Returns:
        int: The ending position of the block.
    """
    lines = text[start:].split("\n")
    end = start
    indent = len(lines[0]) - len(lines[0].lstrip())

    for line in lines[1:]:
        if line.strip() and len(line) - len(line.lstrip()) <= indent:
            break
        end += len(line) + 1

    return end + len(lines[0])


def write_to_file(file_path: str, content: str) -> None:
    """
    Write content to a file.

    Args:
        file_path (str): The path to the file.
        content (str): The content to write.
    """
    with open(file_path, "w") as file:
        file.write(content)


def replace_function_name(
    code: str,
    old_name: str,
    new_name: str,
) -> str:
    """
    Replace the function or class name in the code.
    """
    return re.sub(rf"\b{old_name}\b", new_name, code)


def run_script(script: str, timeout: int = 60) -> Tuple[bool, str]:
    """
    Run the script and return the result.

    Args:
        script (str): The path to the script.
        timeout (int): The maximum time to run the script.

    Returns:
        Tuple[bool, str]: A tuple containing a boolean indicating success and a message.
    """
    try:
        result = subprocess.run(
            ["python", script],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode == 0:
            return True, "All tests passed."
        else:
            return False, f"Tests failed. Output:\n{result.stdout}\n{result.stderr}"
    except subprocess.TimeoutExpired:
        return False, "Test execution timed out."
    except Exception as e:
        return False, f"Error running tests: {str(e)}"
