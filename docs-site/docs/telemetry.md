# Telemetry Guide

**canvodpy** uses [OpenTelemetry](https://opentelemetry.io/) for performance monitoring, metrics collection, and distributed tracing.

---

## Overview

OpenTelemetry provides:
- **Metrics** - Time-series data (duration, throughput, counts)
- **Traces** - Distributed request tracking
- **Automatic Instrumentation** - HTTP, SQLite, threading
- **Custom Instrumentation** - Application-specific metrics

Combined with **Prometheus** (storage) and **Grafana** (visualization), you get production-grade monitoring.

---

## Quick Start

### 1. Start Monitoring Stack

```bash
cd /Users/work/Developer/GNSS/canvodpy

# Start Prometheus + Grafana
docker-compose -f monitoring/docker-compose.yml up -d

# Verify services
docker-compose -f monitoring/docker-compose.yml ps
```

Expected output:
```
NAME                COMMAND                  SERVICE     STATUS
canvodpy-grafana    "/run.sh"               grafana     Up
canvodpy-prometheus "/bin/prometheus --c…"  prometheus  Up
```

### 2. Run with Telemetry

```bash
# Basic usage
opentelemetry-instrument \
    --metrics_exporter prometheus \
    --service_name canvodpy \
    uv run python your_script.py

# With all exporters
opentelemetry-instrument \
    --traces_exporter console \
    --metrics_exporter prometheus \
    --logs_exporter console \
    --service_name canvodpy \
    uv run python your_script.py
```

### 3. Access Dashboards

- **Grafana:** http://localhost:3000
  - Username: `admin`
  - Password: `canvodpy`
- **Prometheus:** http://localhost:9090
- **Metrics Endpoint:** http://localhost:9464/metrics

### 4. View Metrics

1. Open Grafana: http://localhost:3000
2. Navigate to: Dashboards → Canvodpy Performance Dashboard
3. You'll see:
   - Icechunk write duration (avg, P95, P99)
   - Processing throughput (files/sec)
   - RINEX processing times
   - Auxiliary operations

---

## Architecture

```
┌─────────────────────────────────────────┐
│         canvodpy Application            │
│                                         │
│  ┌────────────────────────────────┐   │
│  │   OpenTelemetry SDK            │   │
│  │   - Auto-instrumentation       │   │
│  │   - Custom metrics             │   │
│  │   - Traces                     │   │
│  └────────────┬───────────────────┘   │
│               │                         │
└───────────────┼─────────────────────────┘
                │
                │ Export metrics
                ▼
     ┌────────────────────┐
     │  Prometheus        │
     │  Port: 9090        │
     │  Storage: 15 days  │
     └──────────┬─────────┘
                │
                │ Query data
                ▼
      ┌───────────────────┐
      │     Grafana       │
      │  Port: 3000       │
      │  - Dashboards     │
      │  - Alerts         │
      └───────────────────┘
```

---

## Automatic Instrumentation

### What's Tracked Automatically

#### 1. HTTP Requests (httpx)

**Metrics:**
- Request duration
- HTTP method (GET, POST)
- Full URL
- Status code
- Unique trace ID

**Relevance to canvodpy:**
- Auxiliary file downloads (SP3, CLK from CDDIS/IGS)
- FTP/HTTP operations
- Network latency

**Example:**
```json
{
  "name": "GET",
  "attributes": {
    "http.method": "GET",
    "http.url": "https://cddis.nasa.gov/archive/gnss/products/...",
    "http.status_code": 200
  },
  "start_time": "2026-02-06T16:29:00Z",
  "end_time": "2026-02-06T16:29:01.4Z"
}
```

#### 2. SQLite Queries

**Metrics:**
- SQL statement (full text)
- Database name
- Query type (CREATE, INSERT, SELECT)
- Duration (microsecond precision)

**Relevance to canvodpy:**
- Metadata table operations
- GNSS satellites cache
- Configuration queries

**Example:**
```json
{
  "name": "SELECT",
  "attributes": {
    "db.system": "sqlite",
    "db.statement": "SELECT * FROM rinex_metadata WHERE hash = ?",
    "db.name": "metadata.db"
  },
  "duration": "0.154ms"
}
```

#### 3. Threading

**Metrics:**
- Thread creation/destruction
- Thread pool utilization
- Concurrent operations

**Relevance to canvodpy:**
- ProcessPoolExecutor usage
- Parallel RINEX processing
- Concurrent auxiliary downloads

---

## Custom Metrics

### Instrumentation Decorator

**Location:** `canvodpy/src/canvodpy/utils/telemetry.py`

```python
from opentelemetry import metrics

# Get meter
meter = metrics.get_meter("canvodpy")

# Create instruments
icechunk_duration = meter.create_histogram(
    name="canvodpy.icechunk.write.duration",
    description="Icechunk write operation duration",
    unit="seconds"
)

icechunk_size = meter.create_histogram(
    name="canvodpy.icechunk.write.size",
    description="Icechunk write dataset size",
    unit="MB"
)
```

### Example: Icechunk Writes

```python
from canvodpy.utils.telemetry import trace_icechunk_write

@trace_icechunk_write
def write_to_icechunk(dataset, group_name):
    # ... write logic ...
    pass

# Automatically records:
# - canvodpy.icechunk.write.duration (seconds)
# - canvodpy.icechunk.write.size (MB)
# - Attributes: group_name, success/failure
```

### Example: RINEX Processing

```python
from opentelemetry import metrics
import time

meter = metrics.get_meter("canvodpy")
processing_duration = meter.create_histogram(
    name="canvodpy.rinex.processing.duration",
    description="RINEX file processing duration",
    unit="seconds"
)

def process_rinex_file(file_path):
    start = time.time()
    try:
        # ... processing logic ...
        duration = time.time() - start
        
        # Record metric
        processing_duration.record(
            duration,
            attributes={
                "file": file_path.name,
                "receiver": "canopy_01",
                "status": "success"
            }
        )
    except Exception as e:
        duration = time.time() - start
        processing_duration.record(
            duration,
            attributes={
                "file": file_path.name,
                "receiver": "canopy_01",
                "status": "failed",
                "error": str(e)
            }
        )
        raise
```

---

## Prometheus Setup

### Configuration

**Location:** `monitoring/prometheus/prometheus.yml`

```yaml
global:
  scrape_interval: 10s      # How often to collect metrics
  evaluation_interval: 10s  # How often to evaluate alerts

scrape_configs:
  - job_name: 'canvodpy'
    static_configs:
      - targets: ['host.docker.internal:9464']  # Metrics endpoint
```

### Alert Rules

**Location:** `monitoring/prometheus/alert_rules.yml`

```yaml
groups:
  - name: canvodpy_performance
    interval: 30s
    rules:
      # Alert if writes are consistently slow
      - alert: IcechunkWriteSlow
        expr: rate(canvodpy_icechunk_write_duration_seconds_sum[5m]) 
              / rate(canvodpy_icechunk_write_duration_seconds_count[5m]) > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Icechunk writes are slow"
          description: "Average write duration is {{ $value }}s"

      # Alert if performance degraded vs yesterday
      - alert: IcechunkWriteDegraded
        expr: |
          (
            rate(canvodpy_icechunk_write_duration_seconds_sum[5m])
            / rate(canvodpy_icechunk_write_duration_seconds_count[5m])
          )
          /
          (
            rate(canvodpy_icechunk_write_duration_seconds_sum[1h] offset 1d)
            / rate(canvodpy_icechunk_write_duration_seconds_count[1h] offset 1d)
          ) > 2
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Icechunk performance degraded"
          description: "Writes are {{ $value }}x slower than yesterday"
```

### Manual Queries

Access Prometheus UI: http://localhost:9090

```promql
# Average write duration (5min window)
rate(canvodpy_icechunk_write_duration_seconds_sum[5m]) 
/ 
rate(canvodpy_icechunk_write_duration_seconds_count[5m])

# 95th percentile
histogram_quantile(0.95, 
  rate(canvodpy_icechunk_write_duration_seconds_bucket[5m])
)

# Total data written in last hour (MB)
increase(canvodpy_icechunk_write_size_MB_sum[1h])

# Write throughput (MB/s)
rate(canvodpy_icechunk_write_size_MB_sum[5m]) 
/ 
rate(canvodpy_icechunk_write_duration_seconds_sum[5m])
```

---

## Grafana Dashboard

### Security Setup

**⚠️ IMPORTANT**: Set a secure admin password before starting Grafana!

```bash
# Set password via environment variable
export GRAFANA_ADMIN_PASSWORD="your-secure-password"
docker-compose -f monitoring/docker-compose.yml up -d

# Or use .env file
cd monitoring
echo "GRAFANA_ADMIN_PASSWORD=your-secure-password" > .env
docker-compose up -d
```

**Default**: If `GRAFANA_ADMIN_PASSWORD` is not set, defaults to `admin` (change immediately after first login!)

**Login**: http://localhost:3000
- Username: `admin`
- Password: `<your-password>` (set via env var) or `admin` (default)

### Pre-built Dashboard

**Location:** `monitoring/grafana/dashboards/canvodpy-performance.json`

**Panels:**

#### 1. Icechunk Write Duration
- **Type:** Graph
- **Metrics:** avg, P95, P99
- **Use:** Detect latency trends

**Query:**
```promql
# Average
rate(canvodpy_icechunk_write_duration_seconds_sum[5m]) 
/ 
rate(canvodpy_icechunk_write_duration_seconds_count[5m])

# P95
histogram_quantile(0.95, 
  rate(canvodpy_icechunk_write_duration_seconds_bucket[5m])
)
```

#### 2. Write Size Distribution
- **Type:** Heatmap
- **Use:** Correlate size with duration

#### 3. Current Write Duration
- **Type:** Gauge
- **Thresholds:**
  - Green: < 5s
  - Yellow: 5-10s
  - Red: > 10s

#### 4. Processing Throughput
- **Type:** Graph
- **Metric:** Files per second
- **Use:** Monitor pipeline capacity

#### 5. Auxiliary Operations
- **Type:** Bar chart
- **Metrics:** Download time, interpolation time
- **Use:** Track external dependencies

### Custom Panels

Add your own panels:

1. Open Grafana: http://localhost:3000
2. Navigate to dashboard
3. Click "Add Panel"
4. Enter PromQL query
5. Configure visualization
6. Save dashboard

**Example: Error Rate**
```promql
sum(rate(canvodpy_operations_total{status="failed"}[5m]))
/
sum(rate(canvodpy_operations_total[5m]))
```

---

## Common Queries

### Performance Analysis

#### Is Icechunk Getting Slower?

**7-day trend:**
```promql
(
  rate(canvodpy_icechunk_write_duration_seconds_sum[1h])
  /
  rate(canvodpy_icechunk_write_duration_seconds_count[1h])
)
/
(
  rate(canvodpy_icechunk_write_duration_seconds_sum[1h] offset 7d)
  /
  rate(canvodpy_icechunk_write_duration_seconds_count[1h] offset 7d)
)
```
Result > 1.5 means 50% slower than a week ago

**Today vs Yesterday:**
```promql
rate(canvodpy_icechunk_write_duration_seconds_sum[5m]) 
/ 
rate(canvodpy_icechunk_write_duration_seconds_count[5m])
```
vs
```promql
rate(canvodpy_icechunk_write_duration_seconds_sum[5m] offset 1d) 
/ 
rate(canvodpy_icechunk_write_duration_seconds_count[5m] offset 1d)
```

#### Throughput Trends

**Files per second:**
```promql
rate(canvodpy_rinex_files_processed_total[5m])
```

**MB per second:**
```promql
rate(canvodpy_icechunk_write_size_MB_sum[5m]) 
/ 
rate(canvodpy_icechunk_write_duration_seconds_sum[5m])
```

#### Find Bottlenecks

**Slowest operations:**
```promql
topk(10,
  rate(canvodpy_icechunk_write_duration_seconds_sum[5m])
  /
  rate(canvodpy_icechunk_write_duration_seconds_count[5m])
)
```

**Highest error rate:**
```promql
topk(10,
  sum by (operation) (
    rate(canvodpy_operations_total{status="failed"}[5m])
  )
)
```

### Resource Utilization

#### Store Size Growth

```promql
# Assuming store size metric exists
rate(canvodpy_store_size_bytes[1h])
```

#### Request Rate

```promql
sum(rate(canvodpy_operations_total[5m]))
```

### SLA Monitoring

#### % of writes under 5 seconds

```promql
sum(rate(canvodpy_icechunk_write_duration_seconds_bucket{le="5"}[5m]))
/
sum(rate(canvodpy_icechunk_write_duration_seconds_count[5m]))
```

Result: 0.95 = 95% of writes complete under 5s

---

## Alerting

### Alert Configuration

**Location:** `monitoring/prometheus/alert_rules.yml`

### Built-in Alerts

#### 1. IcechunkWriteSlow
**Condition:** Average write > 10s for 5 minutes  
**Severity:** Warning  
**Action:** Investigate store fragmentation, hardware

#### 2. IcechunkWriteDegraded
**Condition:** 2x slower than yesterday for 10 minutes  
**Severity:** Warning  
**Action:** Check for regressions, system changes

#### 3. RinexProcessingSlow
**Condition:** Average processing > 60s for 5 minutes  
**Severity:** Warning  
**Action:** Check auxiliary availability, network

### Custom Alerts

Add to `alert_rules.yml`:

```yaml
- alert: HighErrorRate
  expr: |
    sum(rate(canvodpy_operations_total{status="failed"}[5m]))
    /
    sum(rate(canvodpy_operations_total[5m]))
    > 0.05
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "Error rate is {{ $value | humanizePercentage }}"
    description: "More than 5% of operations are failing"
```

### Notification Channels

Install Alertmanager:

```yaml
# monitoring/docker-compose.yml
services:
  alertmanager:
    image: prom/alertmanager:latest
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager/alertmanager.yml:/etc/alertmanager/alertmanager.yml
```

**Alertmanager config:**
```yaml
# monitoring/alertmanager/alertmanager.yml
route:
  receiver: 'email'

receivers:
  - name: 'email'
    email_configs:
      - to: 'alerts@example.com'
        from: 'canvodpy@example.com'
        smarthost: 'smtp.example.com:587'
```

---

## Troubleshooting

### Metrics Not Appearing

#### 1. Check Prometheus Exporter

```bash
# Verify metrics endpoint
curl http://localhost:9464/metrics

# Should show canvodpy metrics
curl http://localhost:9464/metrics | grep canvodpy
```

Expected output:
```
# HELP canvodpy_icechunk_write_duration_seconds Icechunk write duration
# TYPE canvodpy_icechunk_write_duration_seconds histogram
canvodpy_icechunk_write_duration_seconds_bucket{le="0.5"} 10
canvodpy_icechunk_write_duration_seconds_bucket{le="1"} 25
...
```

#### 2. Check Prometheus Target

Open http://localhost:9090/targets

Ensure "canvodpy" target shows **UP**

If down:
```bash
# Check if exporter is running
curl http://localhost:9464/metrics

# Check Prometheus logs
docker-compose -f monitoring/docker-compose.yml logs prometheus

# Check Prometheus can reach exporter
docker exec -it canvodpy-prometheus wget -O- http://host.docker.internal:9464/metrics
```

#### 3. Check Grafana Datasource

1. Open http://localhost:3000
2. Go to Configuration → Data Sources
3. Click "Prometheus"
4. Click "Test" - should show "Data source is working"

If not:
```bash
# Check Grafana logs
docker-compose -f monitoring/docker-compose.yml logs grafana

# Check Prometheus is accessible from Grafana
docker exec -it canvodpy-grafana wget -O- http://prometheus:9090/api/v1/query?query=up
```

### No Data in Dashboard

#### 1. Run canvodpy with telemetry

```bash
# Ensure using opentelemetry-instrument
opentelemetry-instrument \
    --metrics_exporter prometheus \
    uv run python your_script.py
```

#### 2. Wait for data collection

- Scrape interval: 10 seconds
- Need at least 1 minute of data for 5m rate queries
- Let it run for 5-10 minutes for meaningful data

#### 3. Check query manually in Prometheus

Open http://localhost:9090/graph

Try simple query:
```promql
up{job="canvodpy"}
```

Should return `1` if scraping is working

### High Cardinality Issues

If Prometheus uses too much memory:

```bash
# Check metric cardinality
curl http://localhost:9090/api/v1/label/__name__/values | jq .

# Identify high cardinality metrics
curl http://localhost:9464/metrics | \
    awk '{print $1}' | sort | uniq -c | sort -rn | head -20
```

**Solution:** Reduce label cardinality

```python
# Bad - unique file names create high cardinality
processing_duration.record(
    duration,
    attributes={"file": file_path}  # Don't include full path!
)

# Good - use categorical labels
processing_duration.record(
    duration,
    attributes={"receiver": "canopy_01", "status": "success"}
)
```

---

## Best Practices

### 1. Use Histograms for Durations

✅ **DO:**
```python
duration_histogram = meter.create_histogram(
    name="operation.duration",
    unit="seconds"
)
duration_histogram.record(2.5)
```

❌ **DON'T:**
```python
duration_counter = meter.create_counter("operation.duration")
duration_counter.add(2.5)  # Can't calculate percentiles!
```

### 2. Keep Labels Low Cardinality

✅ **DO:**
```python
attributes = {
    "receiver_type": "canopy",  # Few values: canopy, reference
    "status": "success",        # Few values: success, failed
    "operation": "write"        # Few values: read, write, delete
}
```

❌ **DON'T:**
```python
attributes = {
    "file_path": "/full/path/to/file.txt",  # Unique per file!
    "timestamp": "2026-02-06T18:00:00Z",    # Unique per second!
    "session_id": "abc123..."               # Unique per session!
}
```

### 3. Run Monitoring Continuously

```bash
# Keep stack running even when not processing
docker-compose -f monitoring/docker-compose.yml up -d

# Let it collect baseline data for 24h
# Then you can compare new runs to baseline
```

### 4. Set Appropriate Scrape Intervals

- **Development:** 10s (default)
- **Production:** 30s-60s (reduce load)
- **High-frequency:** 5s (detailed analysis)

```yaml
# monitoring/prometheus/prometheus.yml
global:
  scrape_interval: 30s  # Adjust here
```

### 5. Use Rate Functions for Counters

```promql
# Wrong - raw counter value
canvodpy_operations_total

# Correct - rate over time window
rate(canvodpy_operations_total[5m])
```

---

## Advanced Topics

### Distributed Tracing

Export traces to Jaeger:

```bash
# Start Jaeger
docker run -d \
    -p 16686:16686 \
    -p 14268:14268 \
    jaegertracing/all-in-one:latest

# Run with trace export
opentelemetry-instrument \
    --traces_exporter otlp \
    --exporter_otlp_endpoint http://localhost:14268 \
    uv run python your_script.py

# View traces: http://localhost:16686
```

### Long-term Storage

Export to Thanos/Cortex for >15 days retention:

```yaml
# monitoring/docker-compose.yml
services:
  thanos-sidecar:
    image: quay.io/thanos/thanos:latest
    command:
      - sidecar
      - --prometheus.url=http://prometheus:9090
      - --objstore.config-file=/etc/thanos/bucket.yml
```

### Custom Exporters

Export to other backends:

```bash
# Export to Google Cloud Monitoring
pip install opentelemetry-exporter-gcp-monitoring

opentelemetry-instrument \
    --metrics_exporter google_cloud_monitoring \
    uv run python your_script.py

# Export to Datadog
pip install opentelemetry-exporter-datadog

opentelemetry-instrument \
    --metrics_exporter datadog \
    uv run python your_script.py
```

---

## Examples

### Daily Performance Check

```bash
#!/bin/bash
# check_performance.sh

# Query average write duration for last 24h
curl -s 'http://localhost:9090/api/v1/query' \
  --data-urlencode 'query=rate(canvodpy_icechunk_write_duration_seconds_sum[24h]) / rate(canvodpy_icechunk_write_duration_seconds_count[24h])' \
  | jq -r '.data.result[0].value[1]'

# Compare to baseline (7 days ago)
curl -s 'http://localhost:9090/api/v1/query' \
  --data-urlencode 'query=rate(canvodpy_icechunk_write_duration_seconds_sum[24h] offset 7d) / rate(canvodpy_icechunk_write_duration_seconds_count[24h] offset 7d)' \
  | jq -r '.data.result[0].value[1]'
```

### Performance Report

```bash
#!/bin/bash
# performance_report.sh

echo "=== Canvodpy Performance Report ==="
echo "Date: $(date)"
echo ""

echo "Average Write Duration (24h):"
curl -s 'http://localhost:9090/api/v1/query' \
  --data-urlencode 'query=rate(canvodpy_icechunk_write_duration_seconds_sum[24h]) / rate(canvodpy_icechunk_write_duration_seconds_count[24h])' \
  | jq -r '.data.result[0].value[1] + "s"'

echo ""
echo "P95 Write Duration (24h):"
curl -s 'http://localhost:9090/api/v1/query' \
  --data-urlencode 'query=histogram_quantile(0.95, rate(canvodpy_icechunk_write_duration_seconds_bucket[24h]))' \
  | jq -r '.data.result[0].value[1] + "s"'

echo ""
echo "Total Data Written (24h):"
curl -s 'http://localhost:9090/api/v1/query' \
  --data-urlencode 'query=increase(canvodpy_icechunk_write_size_MB_sum[24h])' \
  | jq -r '.data.result[0].value[1] + " MB"'
```

---

## See Also

- [Observability Overview](observability.md) - High-level guide
- [Logging Guide](logging.md) - Structured logging
- [OpenTelemetry Docs](https://opentelemetry.io/docs/) - Upstream documentation
- [Prometheus Docs](https://prometheus.io/docs/) - Query language, configuration
- [Grafana Docs](https://grafana.com/docs/) - Dashboard creation, alerts
