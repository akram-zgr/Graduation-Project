#!/usr/bin/env python3
"""
Quick verification script to check if the test suite is properly set up.
Run this before executing the full test suite to verify the installation.
"""
import sys
import os


def check_dependencies():
    """Check if required dependencies are installed."""
    print("Checking dependencies...")
    
    required_packages = {
        'pytest': 'pytest',
        'flask': 'Flask',
        'sqlalchemy': 'flask-sqlalchemy',
    }
    
    missing = []
    for module, package in required_packages.items():
        try:
            __import__(module)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\nMissing packages: {', '.join(missing)}")
        print("Install with: pip install -r requirements.txt --break-system-packages")
        return False
    
    print("All dependencies installed!\n")
    return True


def check_test_files():
    """Check if all test files exist."""
    print("Checking test files...")
    
    test_files = [
        'tests/conftest.py',
        'tests/test_authentication.py',
        'tests/test_roles_permissions.py',
        'tests/test_chatbot_pipeline.py',
        'tests/test_knowledge_base.py',
        'tests/test_faq_system.py',
        'tests/test_context_memory.py',
        'tests/test_ai_analytics.py',
        'tests/test_university_isolation.py',
        'tests/test_database_integrity.py',
    ]
    
    missing = []
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"  ✓ {test_file}")
        else:
            print(f"  ✗ {test_file} - MISSING")
            missing.append(test_file)
    
    if missing:
        print(f"\nMissing test files: {', '.join(missing)}")
        return False
    
    print("All test files present!\n")
    return True


def check_project_structure():
    """Check if project structure is correct."""
    print("Checking project structure...")
    
    required_dirs = [
        'models',
        'routes',
        'services',
        'templates',
        'static',
        'tests',
    ]
    
    required_files = [
        'app.py',
        'config.py',
        'extensions.py',
        'requirements.txt',
        'pytest.ini',
        'run_tests.py',
        'TESTING.md',
        'README.md',
    ]
    
    all_good = True
    
    for directory in required_dirs:
        if os.path.isdir(directory):
            print(f"  ✓ {directory}/")
        else:
            print(f"  ✗ {directory}/ - MISSING")
            all_good = False
    
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} - MISSING")
            all_good = False
    
    if all_good:
        print("Project structure is correct!\n")
    else:
        print("Some files/directories are missing!\n")
    
    return all_good


def count_tests():
    """Count the number of tests in the test suite."""
    print("Counting tests...")
    
    try:
        import subprocess
        result = subprocess.run(
            ['pytest', '--collect-only', '-q', 'tests/'],
            capture_output=True,
            text=True
        )
        
        lines = result.stdout.split('\n')
        for line in lines:
            if 'test' in line and 'selected' in line:
                print(f"  {line}")
        
        print()
        return True
    except Exception as e:
        print(f"  Could not count tests: {e}\n")
        return False


def main():
    """Run all verification checks."""
    print("=" * 70)
    print("TEST SUITE VERIFICATION")
    print("=" * 70)
    print()
    
    checks = [
        ("Dependencies", check_dependencies),
        ("Test Files", check_test_files),
        ("Project Structure", check_project_structure),
        ("Test Count", count_tests),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"Error during {name} check: {e}\n")
            results.append((name, False))
    
    print("=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{name:.<50} {status}")
    
    print("=" * 70)
    
    if all(result for _, result in results):
        print("\n✓ All checks passed! You can now run the test suite.")
        print("\nRun tests with:")
        print("  pytest tests/ -v")
        print("  or")
        print("  python run_tests.py")
        return 0
    else:
        print("\n✗ Some checks failed. Please fix the issues above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
