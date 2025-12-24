"""
Prometheus Exporter untuk Spam Detection Model
Standalone exporter untuk expose custom metrics
"""

from prometheus_client import start_http_server, Counter, Histogram, Gauge
import time
import psutil
import random

# Metrics yang sama dengan yang ada di inference.py
# digunakan untuk standalone monitoring

# Request metrics
request_counter = Counter(
    'spam_detector_requests_total',
    'Total number of prediction requests'
)

prediction_counter = Counter(
    'spam_detector_predictions_total',
    'Total number of predictions by result',
    ['result']
)

error_counter = Counter(
    'spam_detector_errors_total',
    'Total number of errors'
)

# Performance metrics
response_time_histogram = Histogram(
    'spam_detector_response_time_seconds',
    'Response time in seconds',
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
)

inference_latency_histogram = Histogram(
    'spam_detector_inference_latency_seconds',
    'Model inference latency in seconds',
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0]
)

# Gauges
error_rate_gauge = Gauge(
    'spam_detector_error_rate_percent',
    'Current error rate percentage'
)

cpu_usage_gauge = Gauge(
    'spam_detector_cpu_usage_percent',
    'Current CPU usage percentage'
)

memory_usage_gauge = Gauge(
    'spam_detector_memory_usage_percent',
    'Current memory usage percentage'
)

disk_usage_gauge = Gauge(
    'spam_detector_disk_usage_percent',
    'Current disk usage percentage'
)

request_rate_gauge = Gauge(
    'spam_detector_request_rate_per_minute',
    'Current request rate per minute'
)

active_connections_gauge = Gauge(
    'spam_detector_active_connections',
    'Number of active connections'
)

model_accuracy_gauge = Gauge(
    'spam_detector_model_accuracy',
    'Model accuracy from training'
)


def update_metrics():
    """
    Update all metrics with current system values
    Note: Ini adalah standalone exporter
    Untuk produksi, gunakan metrics dari inference.py
    """
    while True:
        try:
            # Update system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_usage_gauge.set(cpu_percent)
            
            memory = psutil.virtual_memory()
            memory_usage_gauge.set(memory.percent)
            
            disk = psutil.disk_usage('/')
            disk_usage_gauge.set(disk.percent)
            
            # Set model accuracy (dari training)
            model_accuracy_gauge.set(0.9631)
            
            # Simulate some activity untuk demo
            # Dalam produksi, metrics ini akan diupdate oleh inference API
            if random.random() > 0.5:
                request_counter.inc()
                
                if random.random() > 0.7:
                    prediction_counter.labels(result='spam').inc()
                else:
                    prediction_counter.labels(result='ham').inc()
                
                # Random response time
                response_time_histogram.observe(random.uniform(0.01, 0.5))
                inference_latency_histogram.observe(random.uniform(0.001, 0.1))
            
            # Calculate error rate
            total_requests = request_counter._value._value
            total_errors = error_counter._value._value
            
            if total_requests > 0:
                error_rate = (total_errors / total_requests) * 100
                error_rate_gauge.set(error_rate)
            
            time.sleep(5)
            
        except Exception as e:
            print(f"Error updating metrics: {e}")
            time.sleep(5)


if __name__ == '__main__':
    print("=" * 60)
    print("PROMETHEUS EXPORTER - SPAM DETECTION MODEL")
    print("=" * 60)
    print("Author: Yudhistira Paksi (dysnomia)")
    print("Starting exporter on port 8000")
    print("Metrics available at: http://localhost:8000/metrics")
    print("=" * 60)
    print("\nNote: Untuk produksi, gunakan metrics dari inference.py")
    print("Exporter ini hanya untuk demo/testing")
    print("\n")
    
    # Start HTTP server untuk expose metrics
    start_http_server(8000)
    
    # Update metrics loop
    update_metrics()
