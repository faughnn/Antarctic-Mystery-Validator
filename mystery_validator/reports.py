from typing import Dict, Tuple


def generate_simple_report(validation_results: Dict[str, Tuple[bool, str]]) -> None:
    """Generate a simple text report from validation results."""
    print("=" * 80)
    print("VALIDATION RESULTS")
    print("=" * 80)
    print()

    passed_count = 0
    failed_count = 0

    for validation_name, (passed, details) in validation_results.items():
        status = "✓ PASS" if passed else "✗ FAIL"

        print(f"{status} - {validation_name}")

        if details:
            # Indent details for readability
            for line in details.split('\n'):
                if line.strip():
                    print(f"      {line}")

        print()

        if passed:
            passed_count += 1
        else:
            failed_count += 1

    print("=" * 80)
    print(f"Summary: {passed_count} passed, {failed_count} failed")
    print("=" * 80)
