"""
Test runner script to execute all unit tests with coverage report.
"""

import pytest
import sys
import os

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    """Run all tests with coverage."""
    print("Running Genesis Agent CLI Test Suite")
    print("=" * 60)
    
    # Test categories
    test_categories = [
        ("Core Models", ["tests/test_agent_spec_enhanced.py"]),
        ("Parsers", ["tests/test_enhanced_spec_parser.py"]),
        ("Converters", ["tests/test_flow_converter.py"]),
        ("Components", [
            "tests/test_dynamic_component_mapper.py",
            "tests/test_component_loader.py"
        ]),
        ("API Services", ["tests/test_genesis_studio_api.py"]),
        ("CLI Commands", [
            "tests/test_create_command.py",
            "tests/test_list_command.py",
            "tests/test_delete_command.py",
            "tests/test_check_deps_command.py",
            "tests/test_publish_command.py",
            "tests/test_run_command.py"
        ])
    ]
    
    # Run tests by category
    all_passed = True
    for category, test_files in test_categories:
        print(f"\n{category} Tests:")
        print("-" * 40)
        
        for test_file in test_files:
            if os.path.exists(test_file):
                result = pytest.main([
                    test_file,
                    "-v",
                    "--tb=short",
                    "--no-header"
                ])
                if result != 0:
                    all_passed = False
            else:
                print(f"  ⚠️  {test_file} not found")
    
    # Run all tests with coverage
    print("\n" + "=" * 60)
    print("Running Complete Test Suite with Coverage")
    print("=" * 60)
    
    exit_code = pytest.main([
        "tests/",
        "-v",
        "--cov=src",
        "--cov-report=term-missing",
        "--cov-report=html",
        "--cov-report=term:skip-covered",
        "--tb=short"
    ])
    
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("-" * 60)
    
    if exit_code == 0:
        print("✅ All tests passed!")
        print("\n📊 Coverage report generated in htmlcov/index.html")
    else:
        print("❌ Some tests failed!")
        print("\nPlease check the output above for details.")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())