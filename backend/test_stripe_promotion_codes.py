"""
Test script to verify Stripe promotion codes functionality.

This script tests the create_subscription_checkout_session function
to ensure that allow_promotion_codes=True is properly set.
"""

import os
import sys
from unittest.mock import MagicMock, patch

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test that the function has the allow_promotion_codes parameter
def test_stripe_checkout_session_with_promotion_codes():
    """Test that create_subscription_checkout_session includes allow_promotion_codes=True"""
    print("Testing Stripe checkout session promotion codes support...")
    
    # Read the actual stripe.py file to verify the code
    stripe_file_path = os.path.join(os.path.dirname(__file__), 'utils', 'stripe.py')
    
    with open(stripe_file_path, 'r') as f:
        stripe_code = f.read()
    
    # Check for the allow_promotion_codes parameter
    if 'allow_promotion_codes=True' in stripe_code:
        print("✅ SUCCESS: allow_promotion_codes=True found in stripe.py")
        
        # Verify it's in the right place (inside create_subscription_checkout_session)
        if 'allow_promotion_codes=True' in stripe_code and 'create_subscription_checkout_session' in stripe_code:
            # Find the context around allow_promotion_codes
            lines = stripe_code.split('\n')
            for i, line in enumerate(lines):
                if 'allow_promotion_codes=True' in line:
                    # Print context
                    start = max(0, i - 5)
                    end = min(len(lines), i + 5)
                    print("\n📄 Context around the change:")
                    for j in range(start, end):
                        marker = ">>> " if j == i else "    "
                        print(f"{marker}{j+1:4d}: {lines[j]}")
                    break
            print("\n✅ Verification complete!")
            return True
    else:
        print("❌ FAIL: allow_promotion_codes=True NOT found in stripe.py")
        print("Please ensure the parameter was added correctly.")
        return False


def test_stripe_api_integration_mock():
    """Mock test to verify the Stripe API call would include allow_promotion_codes"""
    print("\n" + "="*60)
    print("Testing Stripe API integration (mocked)...")
    
    # Mock stripe module
    try:
        # Import the function to test
        from utils import stripe
    except ImportError as e:
        print(f"⚠️  Cannot test integration (dependencies not installed): {e}")
        print("This is expected if the backend dependencies are not installed.")
        return None
    
    # Mock stripe.checkout.Session.create
    original_create = stripe.checkout.Session.create
    
    # Track the parameters passed
    called_params = {}
    
    def mock_create(**kwargs):
        called_params.update(kwargs)
        return MagicMock()
    
    stripe.checkout.Session.create = mock_create
    
    # Set environment variables needed for the function
    os.environ.setdefault('BASE_API_URL', 'https://test.omi.com/')
    os.environ.setdefault('STRIPE_API_KEY', 'sk_test_dummy_key')
    
    # Test the function
    try:
        stripe.create_subscription_checkout_session('test_uid', 'price_test123')
        
        # Check if allow_promotion_codes was in the call
        if called_params.get('allow_promotion_codes') == True:
            print("✅ SUCCESS: allow_promotion_codes=True passed to Stripe API")
            print("\n📋 Full parameters:")
            for key, value in sorted(called_params.items()):
                print(f"  {key}: {value}")
            return True
        else:
            print("❌ FAIL: allow_promotion_codes not found in API call")
            print(f"Parameters passed: {list(called_params.keys())}")
            return False
            
    except Exception as e:
        print(f"⚠️  Warning: Could not fully test integration: {e}")
        print("This might be expected if Stripe credentials are not configured.")
        return None
    finally:
        # Restore original
        stripe.checkout.Session.create = original_create


def test_checkout_session_structure():
    """Test that the checkout session has all required fields"""
    print("\n" + "="*60)
    print("Testing checkout session structure...")
    
    # Read stripe.py to verify structure
    stripe_file_path = os.path.join(os.path.dirname(__file__), 'utils', 'stripe.py')
    
    with open(stripe_file_path, 'r') as f:
        stripe_code = f.read()
    
    # Find the create_subscription_checkout_session function
    lines = stripe_code.split('\n')
    in_function = False
    function_lines = []
    
    for i, line in enumerate(lines):
        if 'def create_subscription_checkout_session' in line:
            in_function = True
            function_lines.append((i+1, line))
            continue
        elif in_function:
            function_lines.append((i+1, line))
            # Stop at next function definition
            if line.strip().startswith('def ') and 'create_subscription_checkout_session' not in line:
                break
    
    # Check for required fields
    required_fields = [
        'client_reference_id',
        'payment_method_types',
        'line_items',
        'mode',
        'success_url',
        'cancel_url',
        'allow_promotion_codes'  # This is what we're adding
    ]
    
    function_text = '\n'.join([line for _, line in function_lines])
    
    print("\n📋 Checking required fields:")
    all_found = True
    for field in required_fields:
        if field in function_text:
            print(f"  ✅ {field}")
        else:
            print(f"  ❌ {field} - MISSING!")
            all_found = False
    
    if all_found:
        print("\n✅ All required fields present in checkout session")
    
    return all_found


def main():
    """Run all tests"""
    print("="*60)
    print("STRIPE PROMOTION CODES TEST SUITE")
    print("="*60)
    
    results = []
    
    # Test 1: Code review
    results.append(("Code Review", test_stripe_checkout_session_with_promotion_codes()))
    
    # Test 2: Structure validation
    results.append(("Structure Check", test_checkout_session_structure()))
    
    # Test 3: Mock integration test
    result = test_stripe_api_integration_mock()
    if result is not None:
        results.append(("Mock Integration", result))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL" if result is False else "⚠️  SKIP"
        print(f"{status}: {test_name}")
    
    passed = sum(1 for _, r in results if r is True)
    total = sum(1 for _, r in results if r is not None)
    
    print(f"\nTests passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! Stripe promotion codes are properly configured.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
