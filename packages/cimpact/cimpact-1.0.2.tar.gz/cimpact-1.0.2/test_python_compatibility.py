#!/usr/bin/env python3
"""
Test script to check Python 3.11+ compatibility for CImpact dependencies
"""

import sys
import subprocess

def test_python_version():
    """Test if Python version is 3.11+"""
    print(f"Python version: {sys.version}")
    major, minor = sys.version_info[:2]
    
    if major == 3 and minor >= 11:
        print("✓ Python 3.11+ detected")
        return True
    else:
        print("✗ Python 3.11+ required")
        return False

def test_dependency_compatibility():
    """Test if major dependencies can be imported"""
    dependencies = [
        ('numpy', 'import numpy'),
        ('pandas', 'import pandas'),
        ('matplotlib', 'import matplotlib'),
    ]
    
    results = {}
    for dep_name, import_cmd in dependencies:
        try:
            exec(import_cmd)
            results[dep_name] = "✓ Available"
        except ImportError as e:
            results[dep_name] = f"✗ Missing: {e}"
        except Exception as e:
            results[dep_name] = f"✗ Error: {e}"
    
    return results

def main():
    print("=== CImpact Python 3.11+ Compatibility Test ===\n")
    
    # Test Python version
    python_ok = test_python_version()
    print()
    
    # Test dependencies
    print("Testing core dependencies:")
    dep_results = test_dependency_compatibility()
    for dep, status in dep_results.items():
        print(f"  {dep}: {status}")
    
    print(f"\nPython 3.11+ compatibility: {'✓ PASS' if python_ok else '✗ FAIL'}")

if __name__ == "__main__":
    main()
