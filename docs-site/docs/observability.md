# Observability

**canvodpy** provides comprehensive observability through two complementary systems:

1. **Structured Logging** - Detailed execution traces for debugging
2. **OpenTelemetry** - Performance metrics and monitoring

Together, these systems provide complete visibility into your GNSS processing pipeline.

---

## Quick Start

### View Logs
```bash
# Human-readable logs
tail -f canvodpy/.logs/human/main.log

# Machine-readable (JSON) logs
jq 'select(.level == "error")' canvodpy/.logs/machine/full.json

# Component-specific logs
tail -f canvodpy/.logs/component/processor.log
tail -f canvodpy/.logs/component/icechunk.log
```

### Monitor Performance
```bash
# Start monitoring stack (Prometheus + Grafana)
docker-compose -f monitoring/docker-compose.yml up -d

# Run with telemetry
opentelemetry-instrument \
    --metrics_exporter prometheus \
    --service_name canvodpy \
    uv run python your_script.py

# View dashboard
open http://localhost:3000
```

---

## When to Use What

| **Scenario** | **Use** | **Tool** |
|-------------|---------|----------|
| Pipeline failed - need to debug | Logs | `tail -f canvodpy/.logs/human/main.log` |
| Find which file caused error | Logs | `jq 'select(.level == "error")' .logs/machine/full.json` |
| Check SID filtering details | Logs | `grep "sid_filtering" .logs/component/processor.log` |
| Is icechunk getting slower? | Telemetry | Grafana dashboard |
| How many files/sec throughput? | Both | Logs for instant, Telemetry for trends |
| Memory usage over time | Telemetry | Prometheus queries |
| Debugging single run | Logs | Component-specific logs |
| Production monitoring | Telemetry | Grafana + alerts |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    canvodpy                             │
│                                                         │
│  ┌──────────────┐          ┌────────────────┐         │
│  │   Structlog  │          │ OpenTelemetry  │         │
│  │   (Logging)  │          │  (Telemetry)   │         │
│  └──────┬───────┘          └────────┬───────┘         │
│         │                           │                  │
│         │ Writes                    │ Exports          │
│         ▼                           ▼                  │
└─────────────────────────────────────────────────────────┘
          │                           │
          │                           │
  ┌───────▼────────┐          ┌───────▼────────┐
  │  .logs/        │          │  Prometheus    │
  │  ├─ human/     │          │  (Port 9464)   │
  │  ├─ machine/   │          └───────┬────────┘
  │  └─ component/ │                  │
  └────────────────┘                  │
                                      ▼
                              ┌────────────────┐
                              │    Grafana     │
                              │ (Port 3000)    │
                              └────────────────┘
```

---

## Logging vs Telemetry

### Logging
**Purpose:** Detailed execution traces  
**Format:** Text + JSON  
**Retention:** Rotated daily/size-based (7-30 days)  
**Query:** `jq`, `grep`, text search  
**Best For:** Debugging, troubleshooting, understanding what happened

**Example:**
```json
{
  "event": "sid_filtering_complete",
  "matched": 321,
  "unmatched": 0,
  "common_sid_examples": ["C05|B1I|I", "C05|B2b|I"],
  "timestamp": "2026-02-06T18:00:00Z"
}
```

### Telemetry
**Purpose:** Performance metrics and trends  
**Format:** Time-series metrics  
**Retention:** 15 days (configurable)  
**Query:** PromQL  
**Best For:** Monitoring, alerting, performance analysis

**Example:**
```promql
rate(canvodpy_icechunk_write_duration_seconds_sum[5m]) 
/ 
rate(canvodpy_icechunk_write_duration_seconds_count[5m])
# Result: 2.3s average write duration
```

---

## Directory Structure

```
canvodpy/
├── .logs/                          # Log files
│   ├── human/                      # Human-readable
│   │   ├── main.log               # INFO+ logs, daily rotation
│   │   └── errors.log             # Errors only, detailed
│   ├── machine/                    # Machine-readable
│   │   ├── full.json              # Everything, 100MB rotation
│   │   └── performance.json       # Timing metrics
│   ├── component/                  # Per-component
│   │   ├── processor.log          # RINEX processing
│   │   ├── icechunk.log           # Store operations
│   │   └── auxiliary.log          # Auxiliary data
│   └── archive/                    # Rotated logs
│
└── monitoring/                     # Telemetry stack
    ├── docker-compose.yml         # Prometheus + Grafana
    ├── prometheus/
    │   ├── prometheus.yml         # Config
    │   └── alert_rules.yml        # Alerts
    └── grafana/
        ├── datasources/           # Prometheus datasource
        └── dashboards/            # Pre-built dashboards
```

---

## Detailed Guides

- **[Logging Guide](logging.md)** - Complete logging documentation
- **[Telemetry Guide](telemetry.md)** - OpenTelemetry setup and usage

---

## Common Workflows

### Debugging a Failed Run
```bash
# 1. Check errors
jq 'select(.level == "error")' canvodpy/.logs/machine/full.json

# 2. Find which file
jq 'select(.event == "icechunk_write_failed") | .file' \
    canvodpy/.logs/machine/full.json

# 3. Get full context
jq 'select(.file == "ract220.25o")' \
    canvodpy/.logs/component/processor.log
```

### Performance Analysis
```bash
# 1. Start monitoring
docker-compose -f monitoring/docker-compose.yml up -d

# 2. Run pipeline with telemetry
opentelemetry-instrument \
    --metrics_exporter prometheus \
    uv run python your_script.py

# 3. Open Grafana
open http://localhost:3000

# 4. Check "Canvodpy Performance Dashboard"
# - Icechunk write duration trends
# - Processing throughput
# - Performance degradation alerts
```

### Daily Monitoring
```bash
# Check recent errors
tail -100 canvodpy/.logs/human/errors.log

# Check icechunk performance
tail -50 canvodpy/.logs/component/icechunk.log | \
    grep "batch_write_complete"

# Or use telemetry dashboard
open http://localhost:3000
```

---

## Configuration

### Logging
**Location:** `canvodpy/src/canvodpy/logging/logging_config.py`

**Key settings:**
- Log directory: `canvodpy/.logs/`
- Rotation: Daily for human logs, 100MB for machine logs
- Retention: 7-30 days
- Levels: DEBUG for component logs, INFO for human logs

**Environment variables:**
```bash
export CANVODPY_LOG_LEVEL=DEBUG  # Change log level
export CANVODPY_LOG_DIR=/custom/path/  # Custom log directory
```

### Telemetry
**Location:** `monitoring/docker-compose.yml`

**Key settings:**
- Scrape interval: 10 seconds
- Retention: 15 days
- Ports: Prometheus (9090), Grafana (3000), Exporter (9464)

**Environment variables:**
```bash
export OTEL_SERVICE_NAME=canvodpy_prod  # Service name in metrics
export OTEL_METRICS_EXPORTER=prometheus  # Exporter type
```

---

## Best Practices

### Logging
1. ✅ **Use component-specific logs for focused debugging**
   ```bash
   tail -f canvodpy/.logs/component/icechunk.log
   ```

2. ✅ **Query JSON logs programmatically**
   ```bash
   jq 'select(.duration_seconds > 10)' .logs/machine/performance.json
   ```

3. ✅ **Check errors.log daily**
   ```bash
   cat canvodpy/.logs/human/errors.log
   ```

4. ❌ **Don't parse human logs with scripts** - Use JSON logs instead

5. ❌ **Don't commit .logs/ directory** - Already in .gitignore

### Telemetry
1. ✅ **Run monitoring stack continuously**
   ```bash
   docker-compose -f monitoring/docker-compose.yml up -d
   ```

2. ✅ **Let it collect 24h of data before making conclusions**

3. ✅ **Set up alerts for automatic detection**
   - See `monitoring/prometheus/alert_rules.yml`

4. ✅ **Use dashboards for visual trends, not raw numbers**

5. ❌ **Don't rely on single data points** - Look at trends over time

---

## Troubleshooting

### No logs appearing
```bash
# Check log directory exists
ls -la canvodpy/.logs/

# Check permissions
chmod -R u+w canvodpy/.logs/

# Check logging is configured
python -c "from canvodpy.logging import get_logger; log = get_logger('test'); log.info('test')"
```

### Telemetry not working
```bash
# Check Prometheus exporter is running
curl http://localhost:9464/metrics | grep canvodpy

# Check Prometheus target is UP
open http://localhost:9090/targets

# Check docker services
docker-compose -f monitoring/docker-compose.yml ps
```

### Logs too large
```bash
# Check sizes
du -sh canvodpy/.logs/*

# Clean old archives
rm -rf canvodpy/.logs/archive/*

# Adjust retention in logging_config.py
# - Reduce `backupCount` for less retention
# - Reduce `maxBytes` for smaller files
```

---

## Advanced Topics

### Custom Metrics
See [Telemetry Guide - Custom Metrics](telemetry.md#custom-metrics)

### Log Aggregation
See [Logging Guide - Centralized Logging](logging.md#centralized-logging)

### Performance Tuning
- Reduce log verbosity for production: Set `LOG_LEVEL=INFO`
- Disable telemetry for benchmarks: Don't use `opentelemetry-instrument`
- Use async logging for high-throughput scenarios

---

## Support

- **Documentation Issues:** [GitHub Issues](https://github.com/nfb2021/canvodpy/issues)
- **Log Format Questions:** See [Logging Guide](logging.md)
- **Telemetry Setup:** See [Telemetry Guide](telemetry.md)
