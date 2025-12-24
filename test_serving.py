"""
Test script for model serving endpoint

Usage:
  python test_serving.py
"""

import requests
import json
from datetime import datetime

# Configuration
SERVING_URL = "http://localhost:5001"

def test_health():
    """Test health endpoint"""
    print("\n" + "=" * 60)
    print("TEST 1: Health Check")
    print("=" * 60)
    
    try:
        response = requests.get(f"{SERVING_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_single_prediction():
    """Test single text prediction"""
    print("\n" + "=" * 60)
    print("TEST 2: Single Prediction")
    print("=" * 60)
    
    test_text = "CONGRATULATIONS! You have won $1,000,000! Click here to claim your prize!"
    
    try:
        response = requests.post(
            f"{SERVING_URL}/invocations",
            json={"inputs": [test_text]},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Input: {test_text}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_batch_predictions():
    """Test batch predictions"""
    print("\n" + "=" * 60)
    print("TEST 3: Batch Predictions")
    print("=" * 60)
    
    test_texts = [
        "URGENT! Your account will be closed. Verify now at fake-link.com",
        "Hi, can we meet for coffee tomorrow at 3pm?",
        "FREE FREE FREE! Click now to win!",
        "Thanks for your email. I'll review the document and get back to you.",
        "CONGRATULATIONS! You are the WINNER! Claim your prize NOW!",
    ]
    
    try:
        response = requests.post(
            f"{SERVING_URL}/invocations",
            json={"inputs": test_texts},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            results = response.json()
            print("\nResults:")
            print("-" * 60)
            for i, (text, pred) in enumerate(zip(test_texts, results['predictions'])):
                print(f"\n{i+1}. Text: {text[:50]}...")
                print(f"   Prediction: {pred['prediction'].upper()}")
                print(f"   Confidence: {pred['confidence']:.4f}")
        else:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_error_handling():
    """Test error handling"""
    print("\n" + "=" * 60)
    print("TEST 4: Error Handling")
    print("=" * 60)
    
    # Test with invalid input
    try:
        response = requests.post(
            f"{SERVING_URL}/invocations",
            json={"invalid": "data"},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Should return 400
        return response.status_code == 400
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("SPAM DETECTION MODEL SERVING - TEST SUITE")
    print("=" * 60)
    print(f"Serving URL: {SERVING_URL}")
    print(f"Test Time: {datetime.now().isoformat()}")
    
    results = {
        "Health Check": test_health(),
        "Single Prediction": test_single_prediction(),
        "Batch Predictions": test_batch_predictions(),
        "Error Handling": test_error_handling()
    }
    
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    total = len(results)
    passed = sum(results.values())
    
    for test_name, passed_test in results.items():
        status = "✓ PASS" if passed_test else "✗ FAIL"
        print(f"{test_name:.<40} {status}")
    
    print("-" * 60)
    print(f"Total: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    exit(main())
