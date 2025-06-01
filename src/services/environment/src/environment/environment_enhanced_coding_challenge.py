import re
from typing import TYPE_CHECKING, Dict

from loguru import logger

from ..interface_client import InterfaceClient
from ..models.domain import ChallengeDataTrail
from ..models.responses import ChallengeResults
from .base_environment import BaseEnvironment
from .environment_coding_challenge import (
    execute_solution_attempt,
    fix_solution,
    generate_tests,
    solve_problem,
    update_data_trail_attempt,
)
from .environment_registry import environment_registry

if TYPE_CHECKING:
    from .base_environment import BaseEnvironment


async def generate_problem(
    challenge_designer_advanced: InterfaceClient,
    concept: str,
    difficulty_level: str,
    previous_problems: list = None,
) -> str:
    """
    Generate a problem statement for the given concept and difficulty level.

    Args:
        challenge_designer_advanced (InterfaceClient): The advanced challenge designer agent.
        concept (str): the concept for the coding challenge.
        difficulty_level (str): the difficulty level of the coding challenge.
        previous_problems (list, optional): A list of previous problems. Defaults to None.

    Returns:
        str: the generated problem statement.
    """
    challenge_designer_advanced_response = await challenge_designer_advanced.interact(
        concepts=concept,
        difficulty_level=difficulty_level,
        previous_problems=previous_problems,
    )
    logger.debug(
        f"Challenge Designer Advanced Response with {concept} - {difficulty_level}: {challenge_designer_advanced_response}"
    )
    if challenge_designer_advanced_response is None:
        logger.opt(exception=True).error("Problem statement is None. Check the challenge designer advanced response.")
        raise ValueError("Problem statement is None")

    logger.debug(f"Generated Problem Statement: {challenge_designer_advanced_response}")
    return challenge_designer_advanced_response


async def validate_tests(
    test_validator: InterfaceClient,
    problem_statement: str,
    test_cases: str,
) -> str:
    """
    Validate the generated test cases against the problem requirements.

    Args:
        test_validator (InterfaceClient): The test validator agent.
        problem_statement (str): The original problem description
        test_cases (str): The generated test cases to validate

    Returns:
        str: Validation analysis report
    """
    if problem_statement and test_cases:
        validator_response = await test_validator.interact(
            problem_statement=problem_statement,
            test_cases=test_cases,
        )
    else:
        logger.opt(exception=True).error("Problem statement or test cases are None. Check the test validator response.")
        raise ValueError("Problem statement or test cases are None")

    logger.debug(f"Test Validation Report: {validator_response}")
    return validator_response


async def analyze_test_errors(
    test_error_analyzer: InterfaceClient,
    solution_code: str,
    test_output: str,
) -> str:
    """
    Analyze test execution failures and provide detailed feedback.

    Args:
        test_error_analyzer (InterfaceClient): The test error analyzer agent.
        solution_code (str): The solution code being tested
        test_output (str): The output from running the tests

    Returns:
        str: Error analysis report
    """
    if solution_code and test_output:
        analyzer_response = await test_error_analyzer.interact(
            code_under_test=solution_code,
            test_output=test_output,
        )
    else:
        logger.opt(exception=True).error(
            "Solution code or test output are None. Check the test error analyzer response."
        )
        raise ValueError("Solution code or test output are None")

    logger.debug(f"Error Analysis Report: {analyzer_response}")
    return analyzer_response


@environment_registry.register_environment_method(
    "environment_enhanced_coding_challenge",
    "execute_node",
)
async def execute_node(
    self: "BaseEnvironment",
    concept: str,
    difficulty_level: str,
    max_attempts: int = 3,
    num_problems: int = 5,
) -> Dict:
    """
    Run a coding challenge for the given concept and difficulty level.

    Args:
        self (BaseEnvironment): The environment instance.
        concept (str): the concept for the coding challenge.
        difficulty_level (str): the difficulty level of the coding challenge.
        max_attempts (int, optional): the maximum number of attempts to solve the challenge. Defaults to 3.
        num_problems (int, optional): the number of problems to solve. Defaults to 5.

    Returns:
        Dict: the results of the coding challenge.
    """
    # initialize the environment if it is not already initialized
    if not self._initialized:
        await self.initialize()

    challenge_results = ChallengeResults()
    previous_problems = []

    try:
        problem_statement = await generate_problem(
            self.agents["challenge_designer_advanced"],
            concept,
            difficulty_level,
            previous_problems=previous_problems,
        )
        test_cases = await generate_tests(
            self.agents["test_generator"],
            problem_statement,
        )

        # extract problem identifier and update previous_problems
        match = re.search(r"##\s*(.+?)\s*\n", problem_statement)
        if match and match.group(1).strip():
            previous_problems.append(match.group(1).strip())
    except ValueError as e:
        logger.opt(exception=True).error(f"Error in problem generation: {e}")
        return challenge_results

    for problem_num in range(num_problems):
        logger.debug(f"Problem {problem_num + 1} of {num_problems}")
        # validate test cases
        try:
            validation_report = await validate_tests(
                self.agents["test_validator"],
                problem_statement,
                test_cases,
            )

        except ValueError as e:
            logger.opt(exception=True).error(f"Error in test validation: {e}")
            continue
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

                challenge_results.data_trail[attempt].test_validation = validation_report
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
                error_analysis = await analyze_test_errors(
                    self.agents["test_error_analyzer"],
                    solution_code=fixed_solution,
                    test_output=challenge_results.data_trail[final_attempt - 1].output,
                )
                challenge_results.data_trail[final_attempt].test_error_analysis = error_analysis
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
