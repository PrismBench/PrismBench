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

    if challenge_designer_advanced_response is None:
        logger.error("Problem statement is None. Check the challenge designer advanced response.")
        raise ValueError("Problem statement is None")

    logger.info(f"Enhanced challenge designer responded for {concept} - {difficulty_level}")
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
        logger.error("Problem statement or test cases are None. Check the test validator response.")
        raise ValueError("Problem statement or test cases are None")

    logger.info("Test validation report ✅")
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
        logger.error("Solution code or test output are None. Check the test error analyzer response.")
        raise ValueError("Solution code or test output are None")

    logger.info("Error analysis report ✅")
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
    previous_problems: list = None,
    **kwargs,
) -> Dict:
    """
    Run a coding challenge for the given concept and difficulty level.

    Args:
        self (BaseEnvironment): The environment instance.
        concept (str): the concept for the coding challenge.
        difficulty_level (str): the difficulty level of the coding challenge.
        max_attempts (int, optional): the maximum number of attempts to solve the challenge. Defaults to 3.
        previous_problems (list, optional): the previous problems to solve. Defaults to None.

    Returns:
        Dict: the results of the coding challenge.
    """
    # initialize the environment if it is not already initialized
    if not self._initialized:
        await self.initialize()

    challenge_results = ChallengeResults()
    problem_statement = None  # initialize to None in case all attempts fail
    for _ in range(max_attempts):
        logger.info(f"Attempt {_ + 1} of {max_attempts} for {concept} - {difficulty_level} - Problem Generation")
        try:
            problem_statement = await generate_problem(
                self.agents["challenge_designer_advanced"],
                concept,
                difficulty_level,
                previous_problems=previous_problems,
            )
        except ValueError:
            logger.info(f"Error in problem generation for {concept} - {difficulty_level}. Retrying...")
            continue
        else:
            break

    if not problem_statement:
        logger.error(f"Failed to generate problem statement for {concept} - {difficulty_level}")
        return challenge_results

    test_cases = None  # initialize to None in case all attempts fail
    for _ in range(max_attempts):
        logger.info(f"Attempt {_ + 1} of {max_attempts} for {concept} - {difficulty_level} - Test Generation")
        try:
            test_cases = await generate_tests(
                self.agents["test_generator"],
                problem_statement,
            )

            # extract problem identifier and update previous_problems
            match = re.search(r"##\s*(.+?)\s*\n", problem_statement)
            if match and match.group(1).strip():
                previous_problems.append(match.group(1).strip())
        except ValueError:
            logger.info(f"Error in test generation for {concept} - {difficulty_level}. Retrying...")
            continue
        else:
            break

    if not test_cases:
        logger.error(f"Failed to generate test cases for {concept} - {difficulty_level}")
        return challenge_results

    # validate test cases
    validation_report = None  # initialize to None in case all attempts fail
    for _ in range(max_attempts):
        try:
            logger.info(f"Attempt {_ + 1} of {max_attempts} for {concept} - {difficulty_level} - Test Validation")
            validation_report = await validate_tests(
                self.agents["test_validator"],
                problem_statement,
                test_cases,
            )
        except ValueError:
            logger.info(f"Error in test validation for {concept} - {difficulty_level}. Retrying...")
            continue
        else:
            break

    # regular attempts
    for attempt in range(max_attempts):
        logger.info(f"Attempt {attempt + 1} of {max_attempts} - Entire Attempt")

        # create data trail entry
        data_trail_entry = ChallengeDataTrail(
            attempt_num=attempt,
            problem_statement=problem_statement,
            test_cases=test_cases,
        )
        challenge_results.data_trail.append(data_trail_entry)

        # generate solution
        solution_code = None  # initialize to None in case all attempts fail
        for _ in range(max_attempts):
            try:
                logger.info(
                    f"Attempt {_ + 1} of {max_attempts} for {concept} - {difficulty_level} - Solution Generation"
                )
                solution_code = await solve_problem(
                    self.agents["problem_solver"],
                    problem_statement if attempt == 0 else None,
                    challenge_results.data_trail[attempt - 1].error_feedback if attempt > 0 else None,
                )
            except ValueError:
                logger.info(f"Error in solution generation for {concept} - {difficulty_level}. Retrying...")
                continue
            else:
                break

        if not solution_code:
            logger.error(f"Failed to generate solution code for {concept} - {difficulty_level}")
            return challenge_results

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

        fixed_solution = None  # initialize to None in case all attempts fail
        for _ in range(max_attempts):
            try:
                logger.info(f"Attempt {_ + 1} of {max_attempts} for {concept} - {difficulty_level} - Solution Fixing")
                fixed_solution = await fix_solution(
                    self.agents["problem_fixer"],
                    problem_statement,
                    test_cases,
                    current_solution=challenge_results.data_trail[final_attempt - 1].solution_code,
                    error_output=challenge_results.data_trail[final_attempt - 1].output,
                )
            except ValueError:
                logger.info(f"Error in solution fixing for {concept} - {difficulty_level}. Retrying...")
                continue
            else:
                break

        if not fixed_solution:
            logger.error(f"Failed to fix solution for {concept} - {difficulty_level}")
            return challenge_results

        error_analysis = None  # initialize to None in case all attempts fail
        for _ in range(max_attempts):
            try:
                logger.info(f"Attempt {_ + 1} of {max_attempts} for {concept} - {difficulty_level} - Error Analysis")
                error_analysis = await analyze_test_errors(
                    self.agents["test_error_analyzer"],
                    solution_code=fixed_solution,
                    test_output=challenge_results.data_trail[final_attempt - 1].output,
                )
                challenge_results.data_trail[final_attempt].test_error_analysis = error_analysis
            except ValueError:
                logger.info(f"Error in error analysis for {concept} - {difficulty_level}. Retrying...")
                continue
            else:
                break

        if not error_analysis:
            logger.error(f"Failed to generate error analysis for {concept} - {difficulty_level}")
            return challenge_results

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

    await self.reset()
    return challenge_results
