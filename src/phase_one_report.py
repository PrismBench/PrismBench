from analysis import (
    PhaseOneAnalyzer,
    PhaseThreeAnalyzer,
    PhaseTwoAnalyzer,
    PhaseOneAndTwoAnalyzer,
)


def main():
    """Generate Phase One analysis report"""
    phase_one_analyzer = PhaseOneAnalyzer(
        "/Users/ahvra/Nexus/Prism/experiments/llama3.1-405b/final-3"
    )
    phase_one_analyzer.generate_report()
    print("Report generated successfully!")

    phase_one_and_two_analyzer = PhaseOneAndTwoAnalyzer(
        "/Users/ahvra/Nexus/Prism/experiments/llama3.1-405b/final-3"
    )
    phase_one_and_two_analyzer.generate_report()
    print("Phase One and Two report generated successfully!")
    phase_two_analyzer = PhaseTwoAnalyzer(
        "/Users/ahvra/Nexus/Prism/experiments/llama3.1-405b/final-3"
    )
    phase_two_analyzer.generate_report()
    print("Phase Two report generated successfully!")

    phase_three_analyzer = PhaseThreeAnalyzer(
        "/Users/ahvra/Nexus/Prism/experiments/llama3.1-405b/final-3"
    )
    phase_three_analyzer.generate_report()


if __name__ == "__main__":
    main()
