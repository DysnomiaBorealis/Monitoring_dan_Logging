"""
Inference API untuk Spam Detection Model
dengan Prometheus Metrics Integration
"""

from flask import Flask, request, jsonify
from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY
import joblib
import time
import psutil
import os
import requests
from datetime import datetime


app = Flask(__name__)

# ==================================================================
# SERVING ENDPOINT CONFIGURATION
# ==================================================================
# Instead of loading model locally, we use the Docker serving endpoint
# This follows MLOps best practice: inference API calls serving endpoint

SERVING_URL = os.getenv('SERVING_URL', 'http://localhost:5001')

print("=" * 60)
print("SPAM DETECTION INFERENCE API")
print("=" * 60)
print(f"Using model serving endpoint: {SERVING_URL}")
print("Verifying endpoint availability...")

try:
    import requests
    response = requests.get(f"{SERVING_URL}/health", timeout=5)
    if response.status_code == 200:
        health = response.json()
        if health.get('status') == 'healthy':
            print("[OK] Serving endpoint is healthy and ready!")
        else:
            print("[WARNING] Serving endpoint returned unhealthy status")
    else:
        print(f"[WARNING] Serving endpoint returned status code {response.status_code}")
except Exception as e:
    print(f"[WARNING] Could not connect to serving endpoint: {e}")
    print("  Make sure the serving container is running:")
    print("  Run: .\\setup_serving.ps1")

print("=" * 60)


# ==================================================================
# PROMETHEUS METRICS (10+ metrics untuk Advance)
# ==================================================================

# 1. Request Counter
request_counter = Counter(
    'spam_detector_requests_total',
    'Total number of prediction requests'
)

# 2-3. Prediction Counters (spam dan ham terpisah)
prediction_counter = Counter(
    'spam_detector_predictions_total',
    'Total number of predictions by result',
    ['result']  # label: spam/ham
)

# 4. Error Counter
error_counter = Counter(
    'spam_detector_errors_total',
    'Total number of errors'
)

# 5. Response Time Histogram
response_time_histogram = Histogram(
    'spam_detector_response_time_seconds',
    'Response time in seconds',
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
)

# 6. Inference Latency Histogram
inference_latency_histogram = Histogram(
    'spam_detector_inference_latency_seconds',
    'Model inference latency in seconds',
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0]
)

# 7. Error Rate Gauge
error_rate_gauge = Gauge(
    'spam_detector_error_rate_percent',
    'Current error rate percentage'
)

# 8. CPU Usage Gauge
cpu_usage_gauge = Gauge(
    'spam_detector_cpu_usage_percent',
    'Current CPU usage percentage'
)

# 9. Memory Usage Gauge
memory_usage_gauge = Gauge(
    'spam_detector_memory_usage_percent',
    'Current memory usage percentage'
)

# 10. Disk Usage Gauge
disk_usage_gauge = Gauge(
    'spam_detector_disk_usage_percent',
    'Current disk usage percentage'
)

# 11. Request Rate Gauge
request_rate_gauge = Gauge(
    'spam_detector_request_rate_per_minute',
    'Current request rate per minute'
)

# 12. Active Connections Gauge
active_connections_gauge = Gauge(
    'spam_detector_active_connections',
    'Number of active connections'
)

# 13. Model Accuracy Gauge (dari training)
model_accuracy_gauge = Gauge(
    'spam_detector_model_accuracy',
    'Model accuracy from training'
)

# Set initial accuracy (dari training results)
model_accuracy_gauge.set(0.9631)  # Dari hasil training sebelumnya

# Tracking variabel untuk rate calculation
request_timestamps = []


def update_system_metrics():
    """Update system resource metrics"""
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_usage_gauge.set(cpu_percent)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_usage_gauge.set(memory.percent)
        
        # Disk usage (Windows compatible)
        disk = psutil.disk_usage('C:\\')
        disk_usage_gauge.set(disk.percent)
    except Exception as e:
        print(f"Error updating system metrics: {e}")


def calculate_error_rate():
    """Calculate and update error rate"""
    try:
        total_requests = request_counter._value._value
        total_errors = error_counter._value._value
        
        if total_requests > 0:
            error_rate = (total_errors / total_requests) * 100
            error_rate_gauge.set(error_rate)
    except Exception as e:
        print(f"Error calculating error rate: {e}")


def calculate_request_rate():
    """Calculate requests per minute"""
    try:
        now = time.time()
        # Keep only requests from last minute
        global request_timestamps
        request_timestamps = [ts for ts in request_timestamps if now - ts < 60]
        
        # Calculate rate
        rate = len(request_timestamps)
        request_rate_gauge.set(rate)
    except Exception as e:
        print(f"Error calculating request rate: {e}")


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint - checks both this API and the serving endpoint"""
    try:
        import requests
        serving_health = requests.get(f"{SERVING_URL}/health", timeout=5).json()
        serving_healthy = serving_health.get('status') == 'healthy'
    except:
        serving_healthy = False
    
    return jsonify({
        'status': 'healthy' if serving_healthy else 'degraded',
        'inference_api': 'running',
        'serving_endpoint': 'healthy' if serving_healthy else 'unhealthy',
        'serving_url': SERVING_URL,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/predict', methods=['POST'])
def predict():
    """
    Endpoint untuk prediksi spam detection
    Calls the Docker serving endpoint instead of loading model locally
    
    Input JSON:
    {
        "text": "your message here"
    }
    
    Output JSON:
    {
        "prediction": "spam" or "ham",
        "confidence": 0.95,
        "timestamp": "2025-01-01T00:00:00"
    }
    """
    start_time = time.time()
    
    # Increment active connections
    active_connections_gauge.inc()
    
    try:
        # Increment request counter
        request_counter.inc()
        request_timestamps.append(time.time())
        
        # Update system metrics
        update_system_metrics()
        
        # Validate request
        if not request.json or 'text' not in request.json:
            error_counter.inc()
            calculate_error_rate()
            active_connections_gauge.dec()
            return jsonify({'error': 'Missing text field'}), 400
        
        text = request.json['text']
        
        if not text or not isinstance(text, str):
            error_counter.inc()
            calculate_error_rate()
            active_connections_gauge.dec()
            return jsonify({'error': 'Invalid text input'}), 400
        
        # Inference timing
        inference_start = time.time()
        
        # Call serving endpoint instead of local model
        try:
            import requests
            serving_response = requests.post(
                f"{SERVING_URL}/invocations",
                json={"inputs": [text]},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if serving_response.status_code != 200:
                raise Exception(f"Serving endpoint returned {serving_response.status_code}")
            
            serving_result = serving_response.json()
            prediction_data = serving_result['predictions'][0]
            
            result = prediction_data['prediction']
            confidence = prediction_data['confidence']
            
        except Exception as serving_error:
            error_counter.inc()
            calculate_error_rate()
            active_connections_gauge.dec()
            return jsonify({
                'error': f'Serving endpoint error: {str(serving_error)}',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        inference_duration = time.time() - inference_start
        inference_latency_histogram.observe(inference_duration)
        
        # Update prediction counter
        prediction_counter.labels(result=result).inc()
        
        # Calculate metrics
        calculate_error_rate()
        calculate_request_rate()
        
        # Record response time
        response_duration = time.time() - start_time
        response_time_histogram.observe(response_duration)
        
        # Decrement active connections
        active_connections_gauge.dec()
        
        return jsonify({
            'prediction': result,
            'confidence': confidence,
            'inference_time_ms': round(inference_duration * 1000, 2),
            'timestamp': datetime.now().isoformat(),
            'served_by': 'docker_endpoint'
        })
    
    except Exception as e:
        error_counter.inc()
        calculate_error_rate()
        active_connections_gauge.dec()
        
        print(f"Error during prediction: {e}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500



@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus metrics endpoint"""
    # Update metrics before returning
    update_system_metrics()
    calculate_error_rate()
    calculate_request_rate()
    
    return generate_latest(REGISTRY), 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route('/', methods=['GET'])
def home():
    """Home endpoint dengan informasi API"""
    return jsonify({
        'service': 'Spam Detection API',
        'author': 'Yudhistira Paksi (dysnomia)',
        'version': '1.0',
        'endpoints': {
            '/predict': 'POST - Make spam detection prediction',
            '/metrics': 'GET - Prometheus metrics',
            '/health': 'GET - Health check'
        },
        'metrics_tracked': [
            'request_count',
            'prediction_count (spam/ham)',
            'error_count',
            'error_rate',
            'response_time',
            'inference_latency',
            'cpu_usage',
            'memory_usage',
            'disk_usage',
            'request_rate',
            'active_connections',
            'model_accuracy'
        ]
    })


if __name__ == '__main__':
    print("=" * 60)
    print("SPAM DETECTION INFERENCE API")
    print("=" * 60)
    print(f"Author: Yudhistira Paksi (dysnomia)")
    print(f"Starting server on http://localhost:8000")
    print(f"Metrics available at: http://localhost:8000/metrics")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=8000, debug=False)
