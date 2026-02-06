# Canvodpy Monitoring Stack

This directory contains the complete monitoring setup for canvodpy using Prometheus and Grafana.

## 🚀 Quick Start

```bash
# 1. Set Grafana admin password (IMPORTANT!)
export GRAFANA_ADMIN_PASSWORD="your-secure-password-here"

# 2. Start monitoring stack
docker-compose up -d

# 3. Run canvodpy with Prometheus exporter
opentelemetry-instrument \
    --metrics_exporter prometheus \
    --service_name canvodpy \
    uv run python your_script.py

# 3. Access dashboards
# - Grafana: http://localhost:3000 (admin/<your-password>)
# - Prometheus: http://localhost:9090
```

## 🔒 Security Setup

**IMPORTANT**: Set a secure Grafana admin password before starting:

```bash
# Option 1: Export environment variable (recommended)
export GRAFANA_ADMIN_PASSWORD="your-secure-password"
docker-compose up -d

# Option 2: Use .env file
echo "GRAFANA_ADMIN_PASSWORD=your-secure-password" > .env
docker-compose up -d

# Option 3: Inline (less secure, for testing only)
GRAFANA_ADMIN_PASSWORD="test123" docker-compose up -d
```

**Default**: If not set, defaults to `admin` (change immediately after first login!)

## 📁 Directory Structure

```
monitoring/
├── docker-compose.yml          # Container orchestration
├── prometheus/
│   ├── prometheus.yml          # Prometheus configuration
│   └── alert_rules.yml         # Performance alerts
└── grafana/
    ├── datasources/
    │   └── prometheus.yml      # Prometheus datasource
    └── dashboards/
        ├── dashboard.yml       # Dashboard provisioning
        └── canvodpy-performance.json  # Pre-built dashboard
```

## 📊 What's Monitored

- **Icechunk Writes**: Duration, size, throughput
- **RINEX Processing**: Per-file timing, throughput
- **Auxiliary Operations**: Downloads, preprocessing

## 🎯 Key Metrics

| Metric | Description | Unit |
|--------|-------------|------|
| `canvodpy_icechunk_write_duration` | Icechunk write latency | seconds |
| `canvodpy_icechunk_write_size` | Dataset size written | MB |
| `canvodpy_rinex_processing_duration` | RINEX file processing time | seconds |
| `canvodpy_auxiliary_download_duration` | Aux file download time | seconds |

## 🔔 Alerts

- **IcechunkWriteSlow**: Writes > 10s for 5min
- **IcechunkWriteDegraded**: 2x slower than baseline
- **RinexProcessingSlow**: Processing > 60s for 5min

## 📚 Documentation

See `opentelemetry-phase3-complete.md` in session files for:
- Complete setup guide
- PromQL query examples
- Troubleshooting tips
- Advanced usage

## 🛠️ Management

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f prometheus
docker-compose logs -f grafana

# Restart services
docker-compose restart

# Remove all data (⚠️ deletes metrics!)
docker-compose down -v
```

## 🎯 URLs

- **Grafana Dashboard**: http://localhost:3000
  - Login: `admin` / `<your-password>` (set via `GRAFANA_ADMIN_PASSWORD`)
  - Default password: `admin` (if env var not set - **change immediately!**)
- **Prometheus UI**: http://localhost:9090
- **Prometheus Targets**: http://localhost:9090/targets
- **Prometheus Alerts**: http://localhost:9090/alerts

## 💡 Tips

1. Let monitoring run for 24h to establish baselines
2. Check Grafana dashboard daily for trends
3. Alerts automatically detect degradation
4. Export important time ranges before cleanup

## 🔍 Troubleshooting

**No metrics?**
```bash
# Check Prometheus is scraping
curl http://localhost:9464/metrics | grep canvodpy

# Check Prometheus targets
open http://localhost:9090/targets
```

**Grafana dashboard empty?**
- Ensure canvodpy is running with `opentelemetry-instrument`
- Wait 1-2 minutes for initial data
- Check Prometheus datasource in Grafana settings

**Containers not starting?**
```bash
docker-compose logs
```
