#!/usr/bin/env python3
"""
Master Test Script - Run all module tests
Tests all modules in the ATS scoring system
"""

import subprocess
import sys
import os
from pathlib import Path


def run_test(test_script, module_name):
    """Run a test script and return results."""
    print(f"\n{'='*20} TESTING {module_name.upper()} {'='*20}")
    
    try:
        # Check if test script exists
        if not os.path.exists(test_script):
            print(f"❌ Test script not found: {test_script}")
            return False
        
        # Run the test
        result = subprocess.run(
            [sys.executable, test_script],
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )
        
        # Print output
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:", result.stderr)
        
        # Check return code
        if result.returncode == 0:
            print(f"✅ {module_name} tests completed successfully")
            return True
        else:
            print(f"❌ {module_name} tests failed (exit code: {result.returncode})")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {module_name} tests timed out")
        return False
    except Exception as e:
        print(f"❌ Error running {module_name} tests: {e}")
        return False


def main():
    """Run all module tests."""
    print("🧪 ATS SCORING SYSTEM - ALL MODULE TESTS")
    print("="*60)
    
    # Define test scripts
    tests = [
        ("modules/llm/manual_test.py", "LLM"),
        ("modules/qualifications_extractor/manual_test.py", "Qualifications Extractor"),
        ("modules/ats_checker/manual_test.py", "ATS Checker"),
        ("modules/cv_generator/manual_test.py", "CV Generator")
    ]
    
    results = []
    
    # Run each test
    for test_script, module_name in tests:
        success = run_test(test_script, module_name)
        results.append((module_name, success))
    
    # Summary
    print("\n" + "="*60)
    print("📊 OVERALL TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"Modules tested: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {total - passed}")
    
    print("\nDetailed Results:")
    for module_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} - {module_name}")
    
    if passed == total:
        print("\n🎉 ALL MODULES PASSED!")
        print("\n💡 Next steps:")
        print("- Run full workflow: python ats_workflow.py job_description.txt")
        print("- Test individual features as needed")
    else:
        print(f"\n⚠️  {total - passed} MODULE(S) FAILED")
        print("\n🔧 Troubleshooting:")
        print("- Check that you're running from project root")
        print("- Verify GROQ_API_KEY is set in .env")
        print("- Install missing dependencies: pip install -r requirements.txt")
        print("- For Playwright: pip install playwright && playwright install")
    
    print("\n📚 Individual Module Tests:")
    for test_script, module_name in tests:
        print(f"- {module_name}: python {test_script}")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)