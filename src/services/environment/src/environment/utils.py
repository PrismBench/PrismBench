import asyncio
import os
import re
import subprocess
import uuid
from concurrent.futures import ProcessPoolExecutor
from typing import Tuple

from loguru import logger

from .base_environment import BaseEnvironment


def get_output_file_path(
    output_dir: str,
    attempt: int,
) -> str:
    """
    Get a unique file path for the current attempt.

    Args:
        output_dir (str): The directory to save the output file
        attempt (int): The current attempt number

    Returns:
        str: Path to the test file
    """
    unique = uuid.uuid4().hex
    return os.path.join(
        output_dir,
        f"attempt_{attempt}_{unique}_combined_code.py",
    )


def extract_content_from_text(
    text: str,
    start_delimiter: str,
    end_delimiter: str,
) -> str:
    """
    Extract content between two delimiters from text.

    Args:
        text (str): The text to extract content from
        start_delimiter (str): The starting delimiter
        end_delimiter (str): The ending delimiter

    Returns:
        str: The extracted content, or None if not found
    """
    try:
        pattern = f"{start_delimiter}(.*?){end_delimiter}"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
    except Exception as e:
        logger.error(f"Error extracting content: {e}")
    return None


def replace_function_name(
    code: str,
    old_name: str,
    new_name: str,
) -> str:
    """
    Replace a function name in code.

    Args:
        code (str): The code to modify
        old_name (str): The old function name
        new_name (str): The new function name

    Returns:
        str: The modified code
    """
    try:
        # Replace function definition
        code = re.sub(rf"def\s+{old_name}\s*\(", f"def {new_name}(", code)
        # Replace function calls
        code = re.sub(rf"\b{old_name}\s*\(", f"{new_name}(", code)
        return code
    except Exception as e:
        logger.error(f"Error replacing function name: {e}")
        return code


def run_script(script_path: str) -> Tuple[bool, str]:
    """
    Run a Python script and capture its output.

    Args:
        script_path (str): Path to the script to run

    Returns:
        Tuple[bool, str]: Success status and output/error message
    """
    try:
        result = subprocess.run(
            ["python", script_path],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            return True, result.stdout or "All tests passed."
        else:
            return False, result.stderr or result.stdout

    except Exception as e:
        logger.error(f"Error running script: {e}")
        return False, str(e)


async def run_script_async(
    process_pool: ProcessPoolExecutor,
    script_path: str,
) -> Tuple[bool, str]:
    """
    Run a script in the shared process pool so multiple attempts
    can execute in parallel without blocking the event loop.

    Args:
        process_pool (ProcessPoolExecutor): The process pool to use
        script_path (str): The path to the script to run

    Returns:
        Tuple[bool, str]: Success status and output/error message
    """
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(process_pool, run_script, script_path)


def create_environment(strategy_name: str, **kwargs) -> BaseEnvironment:
    """
    Create an environment based on the strategy name.

    Args:
        strategy_name (str): The name of the strategy to create
        **kwargs: Additional arguments to pass to the BaseEnvironment constructor
    """
    return BaseEnvironment(environment_name=strategy_name, **kwargs)
