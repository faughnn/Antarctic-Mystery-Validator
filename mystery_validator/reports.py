

def generate_simple_report(validation_results):
    """Generate a simple text report from validation results."""
    print("Generating simple report...")
    print("=" * 100)

    for validation_name, (passed, details) in validation_results.items():
        status = "✓" if passed else "✗"
        print(f"{status} {validation_name}")
        if not passed:
            print(f"Details: {details}")
        print("-" * 100)


