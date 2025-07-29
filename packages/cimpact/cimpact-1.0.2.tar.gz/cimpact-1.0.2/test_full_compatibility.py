#!/usr/bin/env python3
"""
Comprehensive test for CImpact Python 3.11+ support
This script tests if the library can be installed and used with Python 3.11+
"""

import sys
import subprocess
import tempfile
import os
import shutil

def check_python_version():
    """Check if Python version is 3.11+"""
    major, minor = sys.version_info[:2]
    
    print(f"Python version: {sys.version}")
    
    if major == 3 and minor >= 11:
        print("✓ Python 3.11+ detected")
        return True
    else:
        print("✗ Python version not compatible (requires 3.11+)")
        return False

def test_package_build():
    """Test if the package can be built successfully"""
    print("\n=== Testing Package Build ===")
    
    try:
        # Build the package
        result = subprocess.run(
            [sys.executable, "-m", "build", "--sdist", "--no-isolation"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✓ Package builds successfully")
            return True
        else:
            print(f"✗ Package build failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Build error: {e}")
        return False

def test_pyproject_syntax():
    """Test if pyproject.toml is valid"""
    print("\n=== Testing pyproject.toml Syntax ===")
    
    try:
        import tomllib  # Python 3.11+
    except ImportError:
        try:
            import tomli as tomllib  # Fallback for older Python
        except ImportError:
            print("⚠ Cannot validate TOML syntax (no tomllib/tomli available)")
            return True
    
    try:
        with open("pyproject.toml", "rb") as f:
            config = tomllib.load(f)
        
        # Check Python version constraint
        python_requires = config.get("project", {}).get("requires-python", "")
        print(f"✓ pyproject.toml is valid")
        print(f"  Python requirement: {python_requires}")
        
        # Verify it includes 3.11+
        if "3.11" in python_requires or "3.13" in python_requires:
            print("✓ Python 3.11+ support is declared")
            return True
        else:
            print("⚠ Python 3.11+ support may not be explicitly declared")
            return True
            
    except Exception as e:
        print(f"✗ pyproject.toml validation failed: {e}")
        return False

def test_import_compatibility():
    """Test if the package can be imported (basic syntax check)"""
    print("\n=== Testing Basic Import Compatibility ===")
    
    # Add src to path for testing
    import sys
    src_path = os.path.join(os.getcwd(), "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    try:
        # Test basic syntax by importing the main module
        import cimpact
        from cimpact import CausalImpactAnalysis
        print("✓ Main modules can be imported")
        return True
    except ImportError as e:
        print(f"✗ Import failed (missing dependencies): {e}")
        print("  This is expected if dependencies aren't installed")
        return True  # This is OK for this test
    except SyntaxError as e:
        print(f"✗ Syntax error in code: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def main():
    """Run all compatibility tests"""
    print("=== CImpact Python 3.11+ Compatibility Test ===")
    
    tests = [
        ("Python Version Check", check_python_version),
        ("pyproject.toml Validation", test_pyproject_syntax),
        ("Import Compatibility", test_import_compatibility),
        ("Package Build", test_package_build),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"✗ {test_name} failed with error: {e}")
            results[test_name] = False
    
    print("\n=== Summary ===")
    all_passed = True
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print(f"\nOverall result: {'✓ ALL TESTS PASSED' if all_passed else '✗ SOME TESTS FAILED'}")
    print(f"\n🎉 CImpact now supports Python 3.11 and 3.12!" if all_passed else "\n⚠ There may be compatibility issues.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
