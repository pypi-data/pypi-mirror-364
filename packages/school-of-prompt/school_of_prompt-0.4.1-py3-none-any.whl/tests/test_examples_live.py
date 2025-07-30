#!/usr/bin/env python3
"""
Live testing of examples with actual API calls.
Requires OPENAI_API_KEY environment variable.
"""

import os
import subprocess
import sys
from pathlib import Path


def check_api_key():
    """Check if API key is available."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️ OPENAI_API_KEY not set. Skipping live API tests.")
        print(
            "To test with real API calls, set: export OPENAI_API_KEY='sk-your-key-here'"
        )
        return False

    if not api_key.startswith("sk-"):
        print("⚠️ OPENAI_API_KEY doesn't look valid (should start with 'sk-')")
        return False

    print("✅ API key found and appears valid")
    return True


def run_example(example_file):
    """Run an example script and check for success."""
    print(f"🧪 Testing {example_file}...")

    example_path = Path("examples/simple_examples") / example_file
    if not example_path.exists():
        print(f"❌ Example not found: {example_path}")
        return False

    try:
        # Run the example
        result = subprocess.run(
            [sys.executable, example_file],
            cwd="examples/simple_examples",
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode == 0:
            print(f"✅ {example_file} completed successfully")

            # Check for expected output patterns
            output = result.stdout
            if "Best prompt:" in output and "Accuracy:" in output:
                print(f"✅ {example_file} produced expected output format")
                return True
            else:
                print(f"⚠️ {example_file} ran but output format unexpected")
                print("Output:", output[:200] + "..." if len(output) > 200 else output)
                return False
        else:
            print(f"❌ {example_file} failed with exit code {result.returncode}")
            print("Error:", result.stderr)
            return False

    except subprocess.TimeoutExpired:
        print(f"❌ {example_file} timed out (>60s)")
        return False
    except Exception as e:
        print(f"❌ Error running {example_file}: {e}")
        return False


def test_basic_api_call():
    """Test a minimal API call to verify connectivity."""
    print("🧪 Testing basic API connectivity...")

    # Check if API key is available and valid
    import os

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key.startswith("test_key"):
        print("⚠️ No valid OPENAI_API_KEY found. Skipping live API test.")
        pytest = __import__("pytest")
        pytest.skip("Valid OPENAI_API_KEY environment variable not set")

    try:
        import pandas as pd

        from school_of_prompt import optimize

        # Minimal test data
        data = pd.DataFrame(
            [
                {"text": "Good", "label": "positive"},
                {"text": "Bad", "label": "negative"},
            ]
        )

        # Simple test
        results = optimize(
            data=data,
            task="classify sentiment",
            prompts=["Is this {text} positive or negative?"],
            model="gpt-3.5-turbo",
            verbose=False,
        )

        if "best_prompt" in results and "best_score" in results:
            print("✅ Basic API call successful")
            print(f"   Best score: {results['best_score']:.2f}")
            assert True  # Test passed
        else:
            print("❌ API call succeeded but unexpected result format")
            assert False, "API call succeeded but unexpected result format"

    except Exception as e:
        print(f"❌ Basic API call failed: {e}")
        assert False, f"Basic API call failed: {e}"


def main():
    """Run live API tests."""
    print("🚀 Starting Live API Tests")
    print("=" * 40)

    # Check API key first
    if not check_api_key():
        print("\n🔑 Set OPENAI_API_KEY to run live tests")
        return True  # Not a failure, just skipped

    tests = [
        ("Basic API Call", test_basic_api_call),
        ("sentiment_analysis.py", lambda: run_example("sentiment_analysis.py")),
        ("content_moderation.py", lambda: run_example("content_moderation.py")),
        ("age_rating_simple.py", lambda: run_example("age_rating_simple.py")),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        print("-" * 30)

        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 40)
    print("📊 LIVE TEST SUMMARY")
    print("=" * 40)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1

    print(f"\nResult: {passed}/{total} live tests passed")

    if passed == total:
        print("\n🎉 All live tests passed! Examples work with real API.")
        return True
    else:
        print(f"\n🚨 {total - passed} tests failed. Check API integration.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
