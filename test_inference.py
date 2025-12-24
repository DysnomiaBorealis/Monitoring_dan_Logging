"""
Test Script untuk Generate Traffic ke Inference API
Untuk menghasilkan metrics yang bisa dimonitor
"""

import requests
import time
import random
from datetime import datetime

# Test messages
SPAM_MESSAGES = [
    "CONGRATULATIONS! You won $1000000! Click here now!!!",
    "FREE iPHONE! Claim your prize now! Limited time only!",
    "You have been selected as a winner! Call this number immediately!",
    "URGENT! Your account will be closed! Click here to verify!",
    "Make money fast! Work from home! Easy money guaranteed!",
    "Get rich quick! No experience needed! Start earning today!",
    "PROMO DISKON 90%! KLIK SEKARANG! TERBATAS!",
    "ANDA MENANG UNDIAN! TRANSFER SEKARANG!",
]

HAM_MESSAGES = [
    "Hi, how are you doing today?",
    "Let's meet for lunch tomorrow at 12pm",
    "The meeting has been rescheduled to next Monday",
    "Can you please send me the report by end of day?",
    "Thank you for your help with the project",
    "Happy birthday! Hope you have a wonderful day!",
    "Halo, apa kabar? Besok kita meeting ya",
    "Terima kasih sudah bantu saya kemarin",
]

def make_prediction(text, should_fail=False):
    """Make a prediction request"""
    url = 'http://localhost:5000/predict'
    
    try:
        if should_fail:
            # Send invalid request to generate error
            response = requests.post(url, json={})
        else:
            response = requests.post(url, json={'text': text})
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Prediction: {result['prediction']} "
                  f"(confidence: {result['confidence']:.2f}, "
                  f"time: {result['inference_time_ms']:.2f}ms)")
            return True
        else:
            print(f"✗ Error: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"✗ Request failed: {e}")
        return False


def generate_traffic(num_requests=100, delay=0.1, error_rate=0.05):
    """
    Generate traffic untuk testing
    
    Args:
        num_requests: Jumlah request yang akan dibuat
        delay: Delay antar request (detik)
        error_rate: Persentase request yang akan error (0.0-1.0)
    """
    print("=" * 70)
    print("TRAFFIC GENERATOR - SPAM DETECTION API")
    print("=" * 70)
    print(f"Author: Yudhistira Paksi (dysnomia)")
    print(f"Target: http://localhost:5000/predict")
    print(f"Requests: {num_requests}")
    print(f"Delay: {delay}s")
    print(f"Error rate: {error_rate * 100}%")
    print("=" * 70)
    print()
    
    success_count = 0
    error_count = 0
    
    for i in range(num_requests):
        # Pilih message secara random
        if random.random() > 0.5:
            message = random.choice(SPAM_MESSAGES)
            expected = "spam"
        else:
            message = random.choice(HAM_MESSAGES)
            expected = "ham"
        
        # Generate error berdasarkan error_rate
        should_fail = random.random() < error_rate
        
        print(f"[{i+1}/{num_requests}] Sending: '{message[:50]}...'")
        
        if make_prediction(message, should_fail):
            success_count += 1
        else:
            error_count += 1
        
        time.sleep(delay)
    
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total requests: {num_requests}")
    print(f"Successful: {success_count}")
    print(f"Failed: {error_count}")
    print(f"Success rate: {(success_count/num_requests)*100:.2f}%")
    print("=" * 70)


def stress_test(duration_seconds=60):
    """
    Stress test untuk generate banyak traffic
    
    Args:
        duration_seconds: Durasi test dalam detik
    """
    print("=" * 70)
    print("STRESS TEST - SPAM DETECTION API")
    print("=" * 70)
    print(f"Duration: {duration_seconds} seconds")
    print(f"Starting at: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 70)
    print()
    
    start_time = time.time()
    request_count = 0
    
    while time.time() - start_time < duration_seconds:
        message = random.choice(SPAM_MESSAGES + HAM_MESSAGES)
        make_prediction(message)
        request_count += 1
        
        # Random delay antara 0.01 - 0.5 detik
        time.sleep(random.uniform(0.01, 0.5))
    
    duration = time.time() - start_time
    rps = request_count / duration
    
    print()
    print("=" * 70)
    print("STRESS TEST SUMMARY")
    print("=" * 70)
    print(f"Duration: {duration:.2f}s")
    print(f"Total requests: {request_count}")
    print(f"Requests per second: {rps:.2f}")
    print("=" * 70)


if __name__ == '__main__':
    import sys
    
    print("\n" + "=" * 70)
    print("TEST SCRIPT OPTIONS")
    print("=" * 70)
    print("1. Normal traffic (100 requests)")
    print("2. Extended traffic (500 requests)")
    print("3. Stress test (60 seconds)")
    print("4. Custom")
    print("=" * 70)
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == '1':
        generate_traffic(num_requests=100, delay=0.1, error_rate=0.05)
    elif choice == '2':
        generate_traffic(num_requests=500, delay=0.05, error_rate=0.05)
    elif choice == '3':
        stress_test(duration_seconds=60)
    elif choice == '4':
        num = int(input("Number of requests: "))
        delay = float(input("Delay between requests (seconds): "))
        error_rate = float(input("Error rate (0.0-1.0): "))
        generate_traffic(num_requests=num, delay=delay, error_rate=error_rate)
    else:
        print("Invalid choice. Running default (100 requests)...")
        generate_traffic(num_requests=100, delay=0.1, error_rate=0.05)
