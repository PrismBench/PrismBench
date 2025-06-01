import re
from concurrent.futures import ProcessPoolExecutor
from typing import TYPE_CHECKING, Dict, Tuple

from loguru import logger

from ..interface_client import InterfaceClient
from ..models.domain import ChallengeDataTrail
from ..models.responses import ChallengeResults
from . import utils
from .base_environment import BaseEnvironment
from .environment_registry import environment_registry

if TYPE_CHECKING:
    from .base_environment import BaseEnvironment


def count_test_results(
    output: str,
    test_cases: str,
) -> Tuple[int, int, int]:
    """
    Count the number of tests passed, failed, and errored from the output.

    Args:
        output (str): the output from running the test cases.
        test_cases (str): the test cases for the coding challenge.

    Returns:
        Tuple[int, int, int]: the number of tests passed, failed, and errored.
    """
    if output != "All tests passed.":
        total_tests_match = re.search(r"Ran (\d+) test", output)
        total_tests = int(total_tests_match.group(1)) if total_tests_match else 0

        result_match = re.search(r"FAILED \((.+?)\)", output)
        if result_match:
            result_details = result_match.group(1)
            failures_match = re.search(r"failures=(\d+)", result_details)
            errors_match = re.search(r"errors=(\d+)", result_details)

            tests_failed = int(failures_match.group(1)) if failures_match else 0
            tests_errored = int(errors_match.group(1)) if errors_match else 0
        else:
            tests_failed = tests_errored = 0

        tests_passed = total_tests - (tests_failed + tests_errored)
        return tests_passed, tests_failed, tests_errored
    else:
        total_tests_match = re.findall(r"def\s+test_\w+\s*\(", test_cases)
        total_tests = len(total_tests_match)

        return total_tests, 0, 0


async def generate_problem(
    challenge_designer: InterfaceClient,
    concept: str,
    difficulty_level: str,
) -> str:
    """
    Generate a problem statement for the given concept and difficulty level.

    Args:
        challenge_designer (InterfaceClient): the challenge designer agent.
        concept (str): the concept for the coding challenge.
        difficulty_level (str): the difficulty level of the coding challenge.

    Returns:
        str: the generated problem statement.
    """

    challenge_designer_response = await challenge_designer.interact(
        concepts=concept,
        difficulty_level=difficulty_level,
    )

    if challenge_designer_response is None:
        logger.opt(exception=True).error("Problem statement is None. Check the challenge designer response.")
        raise ValueError("Problem statement is None")

    logger.debug(f"Challenge Designer Response with {concept} - {difficulty_level}: {challenge_designer_response}")

    return challenge_designer_response


async def generate_tests(
    test_generator: InterfaceClient,
    problem_statement: str,
) -> str:
    """
    Generate test cases for the given problem statement.

    Args:
        test_generator (InterfaceClient): the test generator agent.
        problem_statement (str): the problem statement for which to generate test cases.

    Returns:
        str: the generated test cases.
    """
    test_generator_response = await test_generator.interact(
        problem_statement=problem_statement,
    )

    if test_generator_response is None:
        logger.opt(exception=True).error("Test cases are None. Check the test generator response.")
        raise ValueError("Test cases are None")

    try:
        test_cases = utils.replace_function_name(
            code=test_generator_response,
            old_name="function_to_test",
            new_name="solution",
        )
        logger.debug(f"Generated Test Cases: {test_cases}")

        return test_cases
    except Exception as e:
        logger.opt(exception=True).error(f"Error occurred while replacing function name in test cases. {e}")
        raise ValueError("Test cases names were not replaced")


async def solve_problem(
    problem_solver: InterfaceClient,
    problem_statement: str = None,
    error_feedback: str = None,
) -> str:
    """
    Generate a solution for the given problem statement.

    Args:
        problem_solver (InterfaceClient): the problem solver agent.
        problem_statement (str, optional): the problem statement to solve. for the first attempt,
          this is the original problem statement. for subsequent attempts, it is None.
        error_feedback (str, optional): the error feedback from the previous attempt. Defaults to None.

    Returns:
        str: the generated solution code.
    """

    if problem_statement:
        problem_solver_response = await problem_solver.interact(problem_statement=problem_statement)
    elif error_feedback:
        problem_solver_response = await problem_solver.interact(error_feedback=error_feedback)
    else:
        logger.opt(exception=True).error("No input provided for solution generation.")
        raise ValueError("No input provided for solution generation.")

    logger.debug(f"Generated Solution: {problem_solver_response}")

    if problem_solver_response is None:
        logger.opt(exception=True).error("Solution is None. Check the problem solver response.")
        raise ValueError("Solution is None")

    return problem_solver_response


async def fix_solution(
    problem_fixer: InterfaceClient,
    problem_statement: str,
    test_cases: str,
    current_solution: str,
    error_output: str,
) -> str:
    """
    Attempt to fix the solution based on the error output.

    Args:
        problem_fixer (InterfaceClient): the problem fixer agent.
        problem_statement (str): the problem statement for which to fix the solution.
        test_cases (str): the test cases for the problem statement.
        current_solution (str): the current solution that failed.
        error_output (str): the error output from the failed solution.

    Returns:
        str: the fixed solution code.
    """
    problem_fixer_response = await problem_fixer.interact(
        problem_statement=problem_statement,
        test_cases=test_cases,
        current_solution=current_solution,
        error_output=error_output,
    )

    logger.debug(f"Fixed Solution: {problem_fixer_response}")

    if problem_fixer_response is None:
        logger.opt(exception=True).error("Fixed solution is None. Check the problem fixer response.")
        raise ValueError("Fixed solution is None")

    return problem_fixer_response


async def execute_solution_attempt(
    process_pool: ProcessPoolExecutor,
    output_dir: str,
    attempt_num: int,
    solution_code: str,
    test_cases: str,
) -> Tuple[bool, str, int, int, int]:
    """
    Execute a solution attempt and return results.

    Args:
        process_pool (ProcessPoolExecutor): Pool for running scripts
        output_dir (str): Directory for output files
        attempt_num (int): Attempt number for file naming
        solution_code (str): Solution code to test
        test_cases (str): Test cases to run

    Returns:
        Tuple[bool, str, int, int, int]: success, output, tests_passed, tests_failed, tests_errored
    """
    # write to a unique file for this attempt
    test_file_path = utils.get_output_file_path(output_dir, attempt_num)
    with open(test_file_path, "w") as f:
        f.write(solution_code + "\n" + test_cases)

    success, output = await utils.run_script_async(process_pool, test_file_path)
    tests_passed, tests_failed, tests_errored = count_test_results(output, test_cases)

    return success, output, tests_passed, tests_failed, tests_errored


def update_data_trail_attempt(
    data_trail_entry: ChallengeDataTrail,
    solution_code: str,
    success: bool,
    output: str,
    tests_passed: int,
    tests_failed: int,
    tests_errored: int,
    fixed_by_fixer: bool = False,
) -> None:
    """
    Update a data trail entry with attempt results.

    Args:
        data_trail_entry (ChallengeDataTrail): Entry to update
        solution_code (str): Solution code used
        success (bool): Whether the attempt succeeded
        output (str): Output from script execution
        tests_passed (int): Number of tests passed
        tests_failed (int): Number of tests failed
        tests_errored (int): Number of tests errored
        fixed_by_fixer (bool): Whether this was fixed by problem fixer
    """
    data_trail_entry.solution_code = solution_code
    data_trail_entry.success = success
    data_trail_entry.output = output
    data_trail_entry.tests_passed_num = tests_passed
    data_trail_entry.tests_failed_num = tests_failed
    data_trail_entry.tests_errored_num = tests_errored

    if fixed_by_fixer:
        data_trail_entry.fixed_by_problem_fixer = True


@environment_registry.register_environment_method(
    "environment_coding_challenge",
    "execute_node",
)
async def execute_node(
    self: "BaseEnvironment",
    concept: str,
    difficulty_level: str,
    max_attempts: int = 3,
) -> Dict:
    """
    Run a coding challenge for the given concept and difficulty level.

    Args:
        self (BaseEnvironment): The environment instance.
        concept (str): the concept for the coding challenge.
        difficulty_level (str): the difficulty level of the coding challenge.
        max_attempts (int, optional): the maximum number of attempts to solve the challenge. Defaults to 3.

    Returns:
        Dict: the results of the coding challenge.
    """
    # initialize the environment if it is not already initialized
    if not self._initialized:
        await self.initialize()

    challenge_results = ChallengeResults()
    try:
        problem_statement = await generate_problem(
            self.agents["challenge_designer"],
            concept,
            difficulty_level,
        )
        test_cases = await generate_tests(
            self.agents["test_generator"],
            problem_statement,
        )
    except ValueError as e:
        logger.opt(exception=True).error(f"Error in problem generation: {e}")
        return challenge_results

    # regular attempts
    for attempt in range(max_attempts):
        logger.debug(f"Attempt {attempt + 1} of {max_attempts}")

        # create data trail entry
        data_trail_entry = ChallengeDataTrail(
            attempt_num=attempt,
            problem_statement=problem_statement,
            test_cases=test_cases,
        )
        challenge_results.data_trail.append(data_trail_entry)

        # generate solution
        try:
            solution_code = await solve_problem(
                self.agents["problem_solver"],
                problem_statement if attempt == 0 else None,
                challenge_results.data_trail[attempt - 1].error_feedback if attempt > 0 else None,
            )
        except (ValueError, Exception) as e:
            logger.error(f"Error in solution generation: {e}")
            continue

        # execute and update results
        success, output, tests_passed, tests_failed, tests_errored = await execute_solution_attempt(
            self._pool,
            self.output_dir,
            attempt,
            solution_code,
            test_cases,
        )

        update_data_trail_attempt(
            data_trail_entry,
            solution_code,
            success,
            output,
            tests_passed,
            tests_failed,
            tests_errored,
        )

        if success:
            logger.info("Challenge completed successfully!")
            challenge_results.success = True
            break

        # set error feedback for next attempt
        data_trail_entry.error_feedback = f"""
            Your solution failed. Here's the output:
            {output}
            
            Here's your current solution:
            {solution_code}
            
            Please analyze the error, review your current solution, and provide an improved version.
            """

    # final fix attempt if not successful
    if not challenge_results.success:
        final_attempt = len(challenge_results.data_trail)

        # create final attempt entry
        final_data_trail_entry = ChallengeDataTrail(
            attempt_num=final_attempt,
            problem_statement=problem_statement,
            test_cases=test_cases,
        )
        challenge_results.data_trail.append(final_data_trail_entry)

        try:
            fixed_solution = await fix_solution(
                self.agents["problem_fixer"],
                problem_statement,
                test_cases,
                current_solution=challenge_results.data_trail[final_attempt - 1].solution_code,
                error_output=challenge_results.data_trail[final_attempt - 1].output,
            )

            if fixed_solution:
                # execute fixed solution
                success, output, tests_passed, tests_failed, tests_errored = await execute_solution_attempt(
                    self._pool,
                    self.output_dir,
                    final_attempt,
                    fixed_solution,
                    test_cases,
                )

                update_data_trail_attempt(
                    final_data_trail_entry,
                    fixed_solution,
                    success,
                    output,
                    tests_passed,
                    tests_failed,
                    tests_errored,
                    fixed_by_fixer=success,
                )

                if success:
                    challenge_results.success = True

        except ValueError as e:
            logger.error(f"Error in solution fixing: {e}")

    await self.reset()
    return challenge_results
