# Monitoring dan Logging - Spam Detection Model

Monitoring dan alerting system untuk spam detection model menggunakan Prometheus dan Grafana.  
**Dicoding:** https://www.dicoding.com/users/dysnomia

## Deskripsi

Project ini meng-implement complete monitoring stack untuk spam detection model dengan:
- Flask API untuk model serving
- Prometheus untuk metrics collection
- Grafana untuk visualization dan alerting
- 10+ custom metrics
- 3 alerting rules

## Struktur Folder

```
Monitoring_dan_Logging/
├── 1.bukti_serving.png                          (Screenshot model serving)
├── 2.prometheus.yml                             (Prometheus config)
├── 3.prometheus_exporter.py                     (Standalone exporter)
├── 4.bukti monitoring Prometheus/               (Prometheus screenshots - 10+)
├── 5.bukti monitoring Grafana/                  (Grafana screenshots - 10+)
├── 6.bukti alerting Grafana/                    (Alerting screenshots - 6)
├── 7.inference.py                               (Inference API)
├── test_inference.py                            (Traffic generator)
├── requirements.txt                             (Dependencies)
├── vectorizer.joblib                            (TF-IDF vectorizer)
└── README.md                                    (Dokumentasi)
```

## Prerequisites

- Python 3.12
- Prometheus
- Grafana
- Model dari Membangun_Model

## Instalasi

### 1. Install Python Dependencies

```bash
cd Monitoring_dan_Logging
pip install -r requirements.txt
```

### 2. Install Prometheus

**Windows:**
1. Download: https://prometheus.io/download/
2. Extract ke `C:\prometheus`
3. Copy `2.prometheus.yml` ke `C:\prometheus\prometheus.yml`

### 3. Install Grafana

**Windows:**
1. Download: https://grafana.com/grafana/download
2. Install menggunakan installer
3. Service akan otomatis start

## Cara Menggunakan

### Step 1: Start Inference API

Terminal 1:
```bash
cd Monitoring_dan_Logging
python 7.inference.py
```

Server akan berjalan di: http://localhost:5000

**Endpoints:**
- `GET /` - Home page dengan informasi API
- `POST /predict` - Endpoint untuk prediksi
- `GET /metrics` - Prometheus metrics
- `GET /health` - Health check

**Ambil Screenshot `1.bukti_serving.png`**

### Step 2: Start Prometheus

Terminal 2:
```bash
cd C:\prometheus
.\prometheus.exe --config.file=prometheus.yml
```

Prometheus UI: http://localhost:9090

Verify target UP di: http://localhost:9090/targets

### Step 3: Start Grafana

Grafana biasanya sudah auto-start sebagai service.

Open: http://localhost:3000
- Username: admin
- Password: admin (akan diminta ganti)

### Step 4: Configure Grafana

#### 4.1 Add Prometheus Data Source

1. Sidebar → Configuration → Data Sources
2. Click "Add data source"
3. Select "Prometheus"
4. URL: `http://localhost:9090`
5. Click "Save & Test"

#### 4.2 Create Dashboard

1. Sidebar → Create → Dashboard
2. Settings → General
   - Name: `Spam Detection Model - dysnomia`
   - Description: `Monitoring dashboard untuk spam detection model`
3. Save dashboard

#### 4.3 Add Panels (10+ required)

Add panels untuk setiap metric berikut:

1. **Request Count**
   - Panel type: Stat
   - Query: `spam_detector_requests_total`
   - Title: "Total Requests"

2. **Prediction Distribution** - Spam
   - Panel type: Stat
   - Query: `spam_detector_predictions_total{result="spam"}`
   - Title: "Spam Predictions"

3. **Prediction Distribution** - Ham
   - Panel type: Stat
   - Query: `spam_detector_predictions_total{result="ham"}`
   - Title: "Ham Predictions"

4. **Error Rate**
   - Panel type: Gauge
   - Query: `spam_detector_error_rate_percent`
   - Title: "Error Rate (%)"
   - Thresholds: Green (0-2), Yellow (2-5), Red (5+)

5. **Response Time (p50)**
   - Panel type: Graph
   - Query: `histogram_quantile(0.50, rate(spam_detector_response_time_seconds_bucket[1m]))`
   - Title: "Response Time - p50"

6. **Response Time (p95)**
   - Panel type: Graph
   - Query: `histogram_quantile(0.95, rate(spam_detector_response_time_seconds_bucket[1m]))`
   - Title: "Response Time - p95"

7. **Response Time (p99)**
   - Panel type: Graph
   - Query: `histogram_quantile(0.99, rate(spam_detector_response_time_seconds_bucket[1m]))`
   - Title: "Response Time - p99"

8. **CPU Usage**
   - Panel type: Graph
   - Query: `spam_detector_cpu_usage_percent`
   - Title: "CPU Usage (%)"

9. **Memory Usage**
   - Panel type: Graph
   - Query: `spam_detector_memory_usage_percent`
   - Title: "Memory Usage (%)"

10. **Model Accuracy**
    - Panel type: Stat
    - Query: `spam_detector_model_accuracy`
    - Title: "Model Accuracy"

11. **Request Rate**
    - Panel type: Graph
    - Query: `rate(spam_detector_requests_total[1m]) * 60`
    - Title: "Requests per Minute"

### Step 5: Generate Traffic

Terminal 3:
```bash
cd Monitoring_dan_Logging
python test_inference.py
```

Pilih option yang sesuai untuk generate traffic.

**Recommended:** Option 2 (Extended traffic) untuk populate metrics dengan baik.

### Step 6: Take Prometheus Screenshots

Go to http://localhost:9090/graph

Untuk setiap metric, ambil screenshot dan save ke folder `4.bukti monitoring Prometheus/`:

1. `1.monitoring_request_count.png`
2. `2.monitoring_prediction_spam.png`
3. `3.monitoring_prediction_ham.png`
4. `4.monitoring_error_rate.png`
5. `5.monitoring_response_time_p50.png`
6. `6.monitoring_response_time_p95.png`
7. `7.monitoring_response_time_p99.png`
8. `8.monitoring_cpu_usage.png`
9. `9.monitoring_memory_usage.png`
10. `10.monitoring_model_accuracy.png`
11. `11.monitoring_request_rate.png`

### Step 7: Take Grafana Dashboard Screenshots

Go to Grafana dashboard

PENTING: Pastikan username "dysnomia" terlihat di screenshot (pojok kanan atas)

Ambil screenshot setiap panel dan save ke folder `5.bukti monitoring Grafana/`:

1. `1.monitoring_request_count.png`
2. `2.monitoring_prediction_spam.png`
3. `3.monitoring_prediction_ham.png`
4. `4.monitoring_error_rate.png`
5. `5.monitoring_response_time_p50.png`
6. `6.monitoring_response_time_p95.png`
7. `7.monitoring_response_time_p99.png`
8. `8.monitoring_cpu_usage.png`
9. `9.monitoring_memory_usage.png`
10. `10.monitoring_model_accuracy.png`
11. `11.monitoring_request_rate.png`

### Step 8: Configure Alerting (3 rules required)

#### Alert 1: High Error Rate

1. Edit Error Rate panel
2. Click Alert tab
3. Create alert rule:
   - Name: `High Error Rate`
   - Condition: `WHEN avg() OF query(A, 1m, now) IS ABOVE 5`
   - For: 1m
4. Add notification channel
5. Save

**Take screenshots:**
- `6.bukti alerting Grafana/1.rules_high_error_rate.png`
- `6.bukti alerting Grafana/2.notifikasi_high_error_rate.png`

#### Alert 2: Slow Response Time

1. Edit Response Time p99 panel
2. Create alert rule:
   - Name: `Slow Response Time`
   - Condition: `WHEN avg() OF query(A, 2m, now) IS ABOVE 0.5`
   - For: 1m
3. Add notification
4. Save

**Take screenshots:**
- `6.bukti alerting Grafana/3.rules_slow_response_time.png`
- `6.bukti alerting Grafana/4.notifikasi_slow_response_time.png`

#### Alert 3: High Memory Usage

1. Edit Memory Usage panel
2. Create alert rule:
   - Name: `High Memory Usage`
   - Condition: `WHEN avg() OF query(A, 1m, now) IS ABOVE 80`
   - For: 2m
3. Add notification
4. Save

**Take screenshots:**
- `6.bukti alerting Grafana/5.rules_high_memory_usage.png`
- `6.bukti alerting Grafana/6.notifikasi_high_memory_usage.png`

## Metrics yang Ditrack (12 total)

1. `spam_detector_requests_total` - Total requests
2. `spam_detector_predictions_total{result="spam"}` - Spam predictions
3. `spam_detector_predictions_total{result="ham"}` - Ham predictions
4. `spam_detector_errors_total` - Total errors
5. `spam_detector_error_rate_percent` - Error rate
6. `spam_detector_response_time_seconds` - Response time histogram
7. `spam_detector_inference_latency_seconds` - Inference latency
8. `spam_detector_cpu_usage_percent` - CPU usage
9. `spam_detector_memory_usage_percent` - Memory usage
10. `spam_detector_disk_usage_percent` - Disk usage
11. `spam_detector_request_rate_per_minute` - Request rate
12. `spam_detector_model_accuracy` - Model accuracy

## Testing API

### Manual Test

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "CONGRATULATIONS! You won $1000000!"}'
```

### View Metrics

```bash
curl http://localhost:5000/metrics
```

## Kriteria Penilaian

**Advance (4 pts):**
- Model serving via Flask API
- Prometheus monitoring dengan 10+ metrics
- Grafana dashboard dengan 10+ panels
- 3 alerting rules configured
- Username "dysnomia" visible di screenshots

## Troubleshooting

### Prometheus tidak bisa scrape metrics

Check:
1. Inference API running di port 5000
2. Prometheus config correct path
3. Firewall tidak block port 5000

### Grafana tidak connect ke Prometheus

Check:
1. Prometheus running di port 9090
2. Data source URL correct: http://localhost:9090
3. Network connectivity

### Alert tidak firing

1. Generate traffic untuk trigger condition
2. Wait for evaluation period
3. Check alert history di Grafana

## Notes

- Semua screenshots harus menampilkan username "dysnomia"
- Dashboard name harus include "dysnomia"
- Minimal 10 metrics berbeda untuk Advance
- Minimal 3 alerting rules untuk Advance

## License

Educational Project - Dicoding Machine Learning Operations

## Author

Yudhistira Paksi (dysnomia)
- Dicoding: https://www.dicoding.com/users/dysnomia
- GitHub: @DysnomiaBorealis
