import os
import re
from typing import Dict, Tuple, List

from dotenv import load_dotenv
from loguru import logger

import utils
from llm_interface import LLMInterface

load_dotenv()


class CodingChallengeEnvironment:
    def __init__(self, config_path: str):
        """Initialize the CodingChallengeEnvironment with the given config path."""
        self.config_path = config_path

        # Initialize LLM interfaces for different roles
        self.agents = {
            "challenge_designer": LLMInterface(config_path, verbose=False),
            "test_generator": LLMInterface(config_path, verbose=False),
            "problem_solver": LLMInterface(config_path, verbose=False),
            "problem_fixer": LLMInterface(config_path, verbose=False),
        }

        # Set roles for each agent
        for role, agent in self.agents.items():
            agent.set_role(role)

    def generate_problem(
        self,
        concept: str,
        difficulty_level: str,
    ) -> str:
        """
        Generate a problem statement for the given concept and difficulty level.

        Args:
            concept (str): the concept for the coding challenge.
            difficulty_level (str): the difficulty level of the coding challenge.

        Returns:
            str: the generated problem statement.
        """
        problem_statement = None

        while problem_statement is None:
            challenge_designer_response = self.agents["challenge_designer"].interact(
                concepts=concept,
                difficulty_level=difficulty_level,
            )
            logger.debug(
                f"Challenge Designer Response with {concept} - {difficulty_level}: {challenge_designer_response}"
            )
            problem_statement = utils.extract_content_from_text(
                text=challenge_designer_response,
                start_delimiter="<problem_description>",
                end_delimiter="</problem_description>",
            )
            logger.debug(f"Generated Problem Statement: {problem_statement}")

        return problem_statement

    def generate_tests(self, problem_statement: str) -> str:
        """
        Generate test cases for the given problem statement.

        Args:
            problem_statement (str): the problem statement for which to generate test cases.

        Returns:
            str: the generated test cases.
        """
        test_geenrator_response = self.agents["test_generator"].interact(
            problem_statement=problem_statement,
        )
        try:
            test_cases = utils.extract_content_from_text(
                text=test_geenrator_response,
                start_delimiter="<test_code>",
                end_delimiter="</test_code>",
            )
        except test_cases is None:
            test_cases = utils.extract_content_from_text(
                text=test_geenrator_response,
                start_delimiter="<test\\_code>",
                end_delimiter="</test\\_code>",
            )
        if not test_cases:
            return ""
        try:
            test_cases = utils.replace_function_name(
                code=test_cases,
                old_name="function_to_test",
                new_name="solution",
            )
            logger.debug(f"Generated Test Cases: {test_cases}")
        except Exception as e:
            logger.error(f"Error occurred while generating test cases: {e}")
            test_cases = ""

        return test_cases

    def solve_problem(
        self,
        problem_statement: str = None,
        error_feedback: str = None,
    ) -> str:
        """
        Generate a solution for the given problem statement.

        Args:
            problem_statement (str, optional): the problem statement to solve. for the first attempt,
              this is the original problem statement. for subsequent attempts, it is None.
            error_feedback (str, optional): the error feedback from the previous attempt. Defaults to None.

        Returns:
            str: the generated solution code.
        """
        try:
            if problem_statement:
                problem_solver_response = self.agents["problem_solver"].interact(
                    problem_statement=problem_statement
                )
            elif error_feedback:
                problem_solver_response = self.agents["problem_solver"].interact(
                    error_feedback=error_feedback
                )
            else:
                logger.opt(exception=True).error(
                    "No input provided for solution generation."
                )

            solution = utils.extract_content_from_text(
                text=problem_solver_response,
                start_delimiter="<generated_solution>",
                end_delimiter="</generated_solution>",
            )
            logger.debug(f"Generated Solution: {solution}")
        except Exception as e:
            logger.error(f"Error occurred while generating solution: {e}")
            solution = ""
        return solution

    def fix_solution(
        self,
        problem_statement: str,
        test_cases: str,
        current_solution: str,
        error_output: str,
    ) -> str:
        """
        Attempt to fix the solution based on the error output.

        Args:
            problem_statement (str): the problem statement for which to fix the solution.
            test_cases (str): the test cases for the problem statement.
            current_solution (str): the current solution that failed.
            error_output (str): the error output from the failed solution.

        Returns:
            str: the fixed solution code.
        """

        problem_fixer_response = self.agents["problem_fixer"].interact(
            problem_statement=problem_statement,
            test_cases=test_cases,
            current_solution=current_solution,
            error_output=error_output,
        )

        fixed_solution = utils.extract_content_from_text(
            text=problem_fixer_response,
            start_delimiter="<generated_solution>",
            end_delimiter="</generated_solution>",
        )
        logger.debug(f"Fixed Solution: {fixed_solution}")

        return fixed_solution

    def count_test_results(self, output: str, test_cases) -> Tuple[int, int, int]:
        """
        Count the number of tests passed, failed, and errored from the output.

        Args:
            output (str): the output from running the test cases.
            test_cases (_type_): the test cases for the coding challenge.

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

    def run_challenge(
        self,
        concept: str,
        difficulty_level: str,
        max_attempts: int = 3,
    ) -> Dict:
        """
        Run a coding challenge for the given concept and difficulty level.

        Args:
            concept (str): the concept for the coding challenge.
            difficulty_level (str): the difficulty level of the coding challenge.
            max_attempts (int, optional): the maximum number of attempts to solve the challenge. Defaults to 3.

        Returns:
            Dict: the results of the coding challenge.
        """
        data_trail = {i: {} for i in range(max_attempts)}
        problem_statement = self.generate_problem(concept, difficulty_level)
        test_cases = self.generate_tests(problem_statement)

        results = {
            "problem_statement": problem_statement,
            "test_cases": test_cases,
            "solution_code": None,
            "success": False,
            "output": None,
            "cumulative_tests_passed": 0,
            "cumulative_tests_failed": 0,
            "cumulative_tests_errored": 0,
            "fixed_by_problem_fixer": False,
            "attempts_till_success": None,
        }

        for attempt in range(max_attempts):
            print(f"\n--- Attempt {attempt + 1} ---")
            results["attempts_till_success"] = attempt + 1

            solution_code = self.solve_problem(
                problem_statement if attempt == 0 else None,
                results.get("error_feedback", None),
            )

            data_trail[attempt]["solution_code"] = solution_code
            data_trail[attempt]["problem_statement"] = problem_statement
            data_trail[attempt]["test_cases"] = test_cases
            data_trail[attempt]["problem_solver_solution"] = None

            if not solution_code:
                continue

            results["solution_code"] = solution_code

            utils.write_to_file("combined_code.py", solution_code + "\n" + test_cases)
            success, output = utils.run_script("combined_code.py")
            logger.debug(f"Output: {output}")

            tests_passed, tests_failed, tests_errored = self.count_test_results(
                output, test_cases
            )
            results.update(
                {
                    "success": success,
                    "output": output,
                    "cumulative_tests_passed": results["cumulative_tests_passed"]
                    + tests_passed,
                    "cumulative_tests_failed": results["cumulative_tests_failed"]
                    + tests_failed,
                    "cumulative_tests_errored": results["cumulative_tests_errored"]
                    + tests_errored,
                }
            )

            if success:
                print("\nChallenge completed successfully!")
                break

            results[
                "error_feedback"
            ] = f"""
            Your solution failed. Here's the output:
            {output}
            
            Here's your current solution:
            {solution_code}
            
            Please analyze the error, review your current solution, and provide an improved version.
            """

        if not results["success"]:
            fixed_solution = self.fix_solution(
                problem_statement,
                test_cases,
                current_solution=results["solution_code"],
                error_output=results["output"],
            )

            if fixed_solution:
                utils.write_to_file(
                    "combined_code.py", fixed_solution + "\n" + test_cases
                )
                success, output = utils.run_script("combined_code.py")

                tests_passed, tests_failed, tests_errored = self.count_test_results(
                    output, test_cases
                )
                results.update(
                    {
                        "success": success,
                        "output": output,
                        "cumulative_tests_passed": results["cumulative_tests_passed"]
                        + tests_passed,
                        "cumulative_tests_failed": results["cumulative_tests_failed"]
                        + tests_failed,
                        "cumulative_tests_errored": results["cumulative_tests_errored"]
                        + tests_errored,
                    }
                )

                if success:
                    results["fixed_by_problem_fixer"] = True
                    results["solution_code"] = fixed_solution
                    data_trail[attempt]["problem_solver_solution"] = fixed_solution

        self.reset()
        results["data_trail"] = data_trail
        return results

    def reset(self) -> None:
        """Clear the memory of all agents."""
        for agent in self.agents.values():
            agent.clear_memory()

        self.agents = {
            "challenge_designer": LLMInterface(self.config_path, verbose=False),
            "test_generator": LLMInterface(self.config_path, verbose=False),
            "problem_solver": LLMInterface(self.config_path, verbose=False),
            "problem_fixer": LLMInterface(self.config_path, verbose=False),
        }

        for role, agent in self.agents.items():
            agent.set_role(role)

        logger.debug("Agents Restarted.")


class EnhancedCodingChallengeEnvironment(CodingChallengeEnvironment):
    def __init__(self, config_path: str):
        """Initialize the EnhancedCodingChallengeEnvironment with additional agents."""
        super().__init__(config_path)

        # Remove the problem_fixer and challenge_designer agents
        del self.agents["problem_fixer"]
        del self.agents["challenge_designer"]

        # Add new agents for the enhanced workflow
        additional_agents = {
            "challenge_designer_advanced": LLMInterface(config_path, verbose=False),
            "test_validator": LLMInterface(config_path, verbose=False),
            "test_error_analyzer": LLMInterface(config_path, verbose=False),
        }
        self.agents.update(additional_agents)

        # Set roles for new agents
        for role, agent in additional_agents.items():
            agent.set_role(role)

    def generate_problem(
        self,
        concept: str,
        difficulty_level: str,
        previous_problems: list = None,
    ) -> str:
        """
        Generate a problem statement for the given concept and difficulty level.

        Args:
            concept (str): the concept for the coding challenge.
            difficulty_level (str): the difficulty level of the coding challenge.

        Returns:
            str: the generated problem statement.
        """
        problem_statement = None

        while problem_statement is None:
            challenge_designer_response = self.agents[
                "challenge_designer_advanced"
            ].interact(
                concepts=concept,
                difficulty_level=difficulty_level,
                previous_problems=previous_problems,
            )
            logger.debug(
                f"Challenge Designer Response with {concept} - {difficulty_level}: {challenge_designer_response}"
            )
            problem_statement = utils.extract_content_from_text(
                text=challenge_designer_response,
                start_delimiter="<problem_description>",
                end_delimiter="</problem_description>",
            )
            logger.debug(f"Generated Problem Statement: {problem_statement}")

        return problem_statement

    def validate_tests(self, problem_statement: str, test_cases: str) -> str:
        """
        Validate the generated test cases against the problem requirements.

        Args:
            problem_statement (str): The original problem description
            test_cases (str): The generated test cases to validate

        Returns:
            str: Validation analysis report
        """
        validator_response = self.agents["test_validator"].interact(
            problem_statement=problem_statement,
            test_cases=test_cases,
        )
        validation_report = utils.extract_content_from_text(
            text=validator_response,
            start_delimiter="<test_validation>",
            end_delimiter="</test_validation>",
        )
        logger.debug(f"Test Validation Report: {validation_report}")
        return validation_report

    def analyze_test_errors(self, solution_code: str, test_output: str) -> str:
        """
        Analyze test execution failures and provide detailed feedback.

        Args:
            solution_code (str): The solution code being tested
            test_output (str): The output from running the tests

        Returns:
            str: Error analysis report
        """
        analyzer_response = self.agents["test_error_analyzer"].interact(
            code_under_test=solution_code,
            test_output=test_output,
        )
        error_analysis = utils.extract_content_from_text(
            text=analyzer_response,
            start_delimiter="<error_analysis>",
            end_delimiter="</error_analysis>",
        )
        logger.debug(f"Error Analysis Report: {error_analysis}")
        return error_analysis

    def run_challenge(
        self,
        concept: str,
        difficulty_level: str,
        max_attempts: int = 3,
        num_problems: int = 5,
    ) -> List[Dict]:
        """
        Run multiple enhanced coding challenges with validation and analysis steps.

        Args:
            concept (str): The concept for the coding challenges
            difficulty_level (str): The difficulty level of the challenges
            max_attempts (int, optional): Maximum solution attempts per problem. Defaults to 3.
            num_problems (int, optional): Number of different problems to run. Defaults to 5.

        Returns:
            List[Dict]: A list of results for each problem, including validation and analysis reports
        """
        previous_problems = []
        all_results = []

        for problem_num in range(num_problems):
            print(f"\n=== Problem {problem_num + 1} ===")

            # Generate problem and tests
            problem_statement = self.generate_problem(
                concept,
                difficulty_level,
                previous_problems=previous_problems,
            )

            # Extract problem identifier and update previous_problems
            match = re.search(r"##\s*(.+?)\s*\n", problem_statement)
            if match and match.group(1).strip():
                previous_problems.append(match.group(1).strip())

            test_cases = self.generate_tests(problem_statement)

            # Validate test cases
            validation_report = self.validate_tests(problem_statement, test_cases)

            # Initialize results for this problem
            results = {
                "problem_statement": problem_statement,
                "test_cases": test_cases,
                "test_validation": validation_report,
                "solution_code": None,
                "success": False,
                "output": None,
                "error_analysis": None,
                "cumulative_tests_passed": 0,
                "cumulative_tests_failed": 0,
                "cumulative_tests_errored": 0,
                "fixed_by_problem_fixer": False,
                "attempts_till_success": None,
            }

            # Initialize data_trail for this problem
            data_trail = {i: {} for i in range(max_attempts)}

            # Attempt to solve
            for attempt in range(max_attempts):
                print(f"\n--- Attempt {attempt + 1} ---")
                results["attempts_till_success"] = attempt + 1

                solution_code = self.solve_problem(
                    problem_statement if attempt == 0 else None,
                    results.get("error_feedback", None),
                )

                data_trail[attempt].update(
                    {
                        "solution_code": solution_code,
                        "problem_statement": problem_statement,
                        "test_cases": test_cases,
                        "problem_solver_solution": None,
                    }
                )

                if not solution_code:
                    continue

                results["solution_code"] = solution_code

                utils.write_to_file(
                    "combined_code.py", solution_code + "\n" + test_cases
                )
                success, output = utils.run_script("combined_code.py")

                # Analyze test results
                if not success:
                    error_analysis = self.analyze_test_errors(solution_code, output)
                    results["error_analysis"] = error_analysis

                tests_passed, tests_failed, tests_errored = self.count_test_results(
                    output, test_cases
                )
                results.update(
                    {
                        "success": success,
                        "output": output,
                        "cumulative_tests_passed": results["cumulative_tests_passed"]
                        + tests_passed,
                        "cumulative_tests_failed": results["cumulative_tests_failed"]
                        + tests_failed,
                        "cumulative_tests_errored": results["cumulative_tests_errored"]
                        + tests_errored,
                    }
                )

                if success:
                    print("\nChallenge completed successfully!")
                    break

                results[
                    "error_feedback"
                ] = f"""
                Your solution failed. Here's the output:
                {output}
                
                Error Analysis:
                {results["error_analysis"]}
                
                Here's your current solution:
                {solution_code}
                
                Please analyze the error, review your current solution, and provide an improved version.
                """

            # Add data_trail to results
            results["data_trail"] = data_trail
            # Append results to all_results
            all_results.append(results)

        # Reset agents after all problems are completed
        self.reset()
        return all_results

    def reset(self) -> None:
        """Clear the memory of all agents including the enhanced ones."""
        super().reset()

        # Re-initialize the additional agents
        additional_agents = {
            "challenge_designer_advanced": LLMInterface(
                self.config_path, verbose=False
            ),
            "test_validator": LLMInterface(self.config_path, verbose=False),
            "test_error_analyzer": LLMInterface(self.config_path, verbose=False),
        }
        self.agents.update(additional_agents)

        for role, agent in additional_agents.items():
            agent.set_role(role)

        logger.debug("Enhanced Agents Restarted.")


# Usage example
if __name__ == "__main__":
    config_path = os.path.join(os.getcwd(), "agent_configs", "agent_config_v6.yml")

    env = CodingChallengeEnvironment(config_path=config_path)
    results = env.run_challenge("conditionals", "hard")
    if results["success"]:
        print("success")
    else:
        print("failed")
        print(results["output"])
