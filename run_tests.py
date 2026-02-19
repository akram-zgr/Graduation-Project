#!/usr/bin/env python3
"""
Test runner script for the chatbot platform automated test suite.

This script runs all tests and provides a summary of results.
"""
import sys
import subprocess


def run_tests():
    """Run the complete test suite."""
    print("=" * 70)
    print("MULTI-UNIVERSITY AI CHATBOT PLATFORM - AUTOMATED TEST SUITE")
    print("=" * 70)
    print()
    
    # Run pytest
    print("Running all tests...")
    print("-" * 70)
    
    result = subprocess.run(
        ['pytest', 'tests/', '-v'],
        capture_output=False
    )
    
    print("-" * 70)
    print()
    
    if result.returncode == 0:
        print("✓ ALL TESTS PASSED")
        print("=" * 70)
        return 0
    else:
        print("✗ SOME TESTS FAILED")
        print("=" * 70)
        return 1


def run_specific_test_suite(suite_name):
    """Run a specific test suite."""
    test_files = {
        'auth': 'test_authentication.py',
        'roles': 'test_roles_permissions.py',
        'chatbot': 'test_chatbot_pipeline.py',
        'knowledge': 'test_knowledge_base.py',
        'faq': 'test_faq_system.py',
        'context': 'test_context_memory.py',
        'analytics': 'test_ai_analytics.py',
        'isolation': 'test_university_isolation.py',
        'database': 'test_database_integrity.py'
    }
    
    if suite_name not in test_files:
        print(f"Unknown test suite: {suite_name}")
        print(f"Available suites: {', '.join(test_files.keys())}")
        return 1
    
    test_file = test_files[suite_name]
    print(f"Running {suite_name} tests ({test_file})...")
    print("-" * 70)
    
    result = subprocess.run(
        ['pytest', f'tests/{test_file}', '-v'],
        capture_output=False
    )
    
    return result.returncode


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Run specific test suite
        suite_name = sys.argv[1]
        exit_code = run_specific_test_suite(suite_name)
    else:
        # Run all tests
        exit_code = run_tests()
    
    sys.exit(exit_code)
