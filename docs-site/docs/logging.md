# Logging Guide

**canvodpy** uses [structlog](https://www.structlog.org/) for structured logging with a dual-output system designed for both humans and machines.

---

## Overview

### Design Principles

1. **Dual Output** - Both human-readable text and machine-queryable JSON
2. **Component Isolation** - Separate logs per module (processor, icechunk, auxiliary)
3. **Automatic Filtering** - Errors, performance metrics routed automatically
4. **Log Rotation** - Size and time-based rotation with compression
5. **Rich Context** - Every log includes component, site, timestamp, structured data

---

## Log Outputs

### Human Logs (`human/`)

**Purpose:** Quick scanning, tailing, grep/less  
**Format:** Traditional timestamp + level + message + context  
**Level:** INFO and above  
**Rotation:** Daily at midnight, 30 days retention

**Example:**
```
2026-02-06T18:00:22.367663Z INFO     Processing completed [duration_sec=45.2, files_processed=10, site=TEST_SITE]
2026-02-06T18:00:22.367708Z INFO     Data quality check [metrics={'completeness': 0.95}, status=passed]
2026-02-06T18:00:29.111450Z INFO     component_registered [component=Rnxv3Obs, factory=ReaderFactory]
```

**Files:**
- `main.log` - All INFO+ logs
- `errors.log` - Errors only (WARNING+) with full stack traces

### Machine Logs (`machine/`)

**Purpose:** Programmatic analysis, jq queries, LLM processing  
**Format:** JSON (one event per line)  
**Level:** DEBUG and above  
**Rotation:** 100MB size-based, 10 backups

**Example:**
```json
{
  "event": "sid_filtering_complete",
  "matched": 321,
  "unmatched": 0,
  "common_sid_examples": ["C05|B1I|I", "C05|B2b|I", "C06|B1I|I"],
  "rinex_sids": 321,
  "aux_sids": 321,
  "timestamp": "2026-02-06T18:00:00.123456Z",
  "level": "debug",
  "component": "processor",
  "site": "Rosalia"
}
```

**Files:**
- `full.json` - Everything (DEBUG+)
- `performance.json` - Timing metrics only (filtered)

### Component Logs (`component/`)

**Purpose:** Per-module debugging, isolate specific subsystems  
**Format:** Human-readable text  
**Level:** DEBUG and above  
**Rotation:** Daily, 7 days retention

**Files:**
- `processor.log` - RINEX processing pipeline
- `icechunk.log` - Store operations (writes, commits, metadata)
- `auxiliary.log` - Auxiliary data (SP3, CLK downloads/interpolation)

---

## Log Levels

| **Level** | **Use Case** | **Example** |
|----------|-------------|-------------|
| `DEBUG` | Detailed execution traces | `"sid_filtering_complete"`, `"dataset_cleansed"` |
| `INFO` | Normal operations | `"processing_started"`, `"file_written"` |
| `WARNING` | Recoverable issues | `"file_missing_hash"`, `"auxiliary_download_failed"` |
| `ERROR` | Failures requiring attention | `"icechunk_write_failed"`, `"rinex_processing_failed"` |
| `CRITICAL` | System-level failures | Database corruption, disk full |

---

## Usage Examples

### Viewing Logs

#### Real-time Monitoring
```bash
# Watch all activity
tail -f canvodpy/.logs/human/main.log

# Watch only errors
tail -f canvodpy/.logs/human/errors.log

# Watch specific component
tail -f canvodpy/.logs/component/icechunk.log

# Watch with filtering
tail -f canvodpy/.logs/human/main.log | grep "ERROR\|WARNING"
```

#### Quick Checks
```bash
# Last 50 lines
tail -50 canvodpy/.logs/human/main.log

# Search for pattern
grep "icechunk_write" canvodpy/.logs/human/main.log

# Count errors
grep -c "ERROR" canvodpy/.logs/human/main.log
```

### Querying JSON Logs

#### Basic Queries
```bash
# All errors
jq 'select(.level == "error")' canvodpy/.logs/machine/full.json

# Specific event type
jq 'select(.event == "sid_filtering_complete")' \
    canvodpy/.logs/machine/full.json

# Events from specific component
jq 'select(.component == "icechunk")' \
    canvodpy/.logs/machine/full.json

# Events with duration > 10 seconds
jq 'select(.duration_seconds > 10)' \
    canvodpy/.logs/machine/full.json
```

#### Advanced Queries
```bash
# Average processing duration
jq -s 'map(select(.event == "rinex_preprocessing_complete") 
         | .duration_seconds) 
       | add / length' \
    canvodpy/.logs/machine/full.json

# Top 10 slowest operations
jq -s 'map(select(.duration_seconds)) 
       | sort_by(.duration_seconds) 
       | reverse 
       | .[0:10]' \
    canvodpy/.logs/machine/full.json

# Count events by type
jq -s 'group_by(.event) 
       | map({event: .[0].event, count: length}) 
       | sort_by(.count) 
       | reverse' \
    canvodpy/.logs/machine/full.json

# Find all files that failed
jq 'select(.event == "icechunk_write_failed") 
    | .file' \
    canvodpy/.logs/machine/full.json

# Get context for specific file
jq 'select(.file == "ract220.25o")' \
    canvodpy/.logs/component/processor.log
```

#### Performance Analysis
```bash
# Processing throughput over time
jq 'select(.event == "parallel_processing_complete") 
    | {timestamp, throughput_files_per_sec}' \
    canvodpy/.logs/machine/performance.json

# Icechunk write statistics
jq 'select(.event == "batch_write_complete") 
    | {receiver, duration_seconds, total_files, 
       throughput_files_per_sec, actions}' \
    canvodpy/.logs/machine/full.json

# Auxiliary data loading times
jq 'select(.event == "aux_file_load_complete") 
    | {name, duration_seconds, dataset_size}' \
    canvodpy/.logs/machine/performance.json
```

---

## Log Structure

### Common Fields

Every log entry includes:

```json
{
  "event": "string",           // Event name (e.g., "processing_started")
  "timestamp": "ISO8601",      // UTC timestamp
  "level": "debug|info|...",   // Log level
  "component": "string",       // Component name (processor, icechunk, etc.)
  "site": "string",            // Site name (if applicable)
  ...                          // Event-specific fields
}
```

### Event Types

#### Processing Events
```json
{
  "event": "rinex_preprocessing_complete",
  "file": "ract220.25o",
  "duration_seconds": 1.06,
  "dataset_size": {"epoch": 180, "sid": 321},
  "receiver_type": "canopy_01"
}
```

#### Icechunk Events
```json
{
  "event": "batch_write_complete",
  "receiver": "canopy_01",
  "total_files": 96,
  "duration_seconds": 0.18,
  "throughput_files_per_sec": 542.59,
  "actions": {"initial": 0, "written": 5, "appended": 0, "skipped": 91},
  "timings": {
    "batch_check": 0.04,
    "open_session": 0.00,
    "process_data": 0.02,
    "commit": 0.00,
    "metadata": 0.02
  }
}
```

#### Debug Events
```json
{
  "event": "sid_filtering_complete",
  "matched": 321,
  "unmatched": 0,
  "common_sid_examples": ["C05|B1I|I", "C05|B2b|I"],
  "rinex_sids": 321,
  "aux_sids": 321,
  "filtering_strategy": "intersection"
}
```

---

## Configuration

### Location
**File:** `canvodpy/src/canvodpy/logging/logging_config.py`

### Directory Structure
```python
LOG_DIR = Path("canvodpy/.logs")  # Default location

LOG_DIR/
├── human/
│   ├── main.log         # INFO+, daily rotation, 30 days
│   └── errors.log       # ERROR+, 50MB rotation, 5 backups
├── machine/
│   ├── full.json        # DEBUG+, 100MB rotation, 10 backups
│   └── performance.json # Metrics, 50MB rotation, 10 backups
├── component/
│   ├── processor.log    # DEBUG+, daily rotation, 7 days
│   ├── icechunk.log     # DEBUG+, daily rotation, 7 days
│   └── auxiliary.log    # DEBUG+, daily rotation, 7 days
└── archive/             # Rotated logs (automatic)
```

### Environment Variables

```bash
# Change log level
export CANVODPY_LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR

# Custom log directory
export CANVODPY_LOG_DIR=/custom/path/.logs/

# Disable console output
export CANVODPY_LOG_CONSOLE=false

# Change rotation size
export CANVODPY_LOG_MAX_BYTES=104857600  # 100MB (default)
```

### Programmatic Configuration

```python
from canvodpy.logging import configure_logging

# Use defaults
configure_logging()

# Custom log directory
configure_logging(log_dir="/custom/path/.logs")

# Custom console level
configure_logging(console_level="WARNING")
```

---

## Logging from Code

### Basic Usage

```python
from canvodpy.logging import get_logger

# Get logger
log = get_logger(__name__)

# Simple logging
log.info("processing_started")
log.error("processing_failed", error="File not found")

# With context
log.info(
    "file_processed",
    file="data.csv",
    rows=1000,
    duration_seconds=2.5
)
```

### Structured Data

```python
# Always use keyword arguments for structured data
log.debug(
    "sid_filtering_complete",
    matched=321,
    unmatched=5,
    common_sid_examples=["C05|B1I|I", "C05|B2b|I"],
    rinex_sids=326,
    aux_sids=321
)

# Include timing
import time
start = time.time()
# ... do work ...
duration = time.time() - start

log.info(
    "operation_complete",
    duration_seconds=round(duration, 2),
    items_processed=100
)
```

### Component Binding

```python
# Bind component for automatic filtering
log = get_logger(__name__).bind(component="processor")

# All logs now include component="processor"
log.info("started")  # → Goes to processor.log

# Bind multiple fields
log = get_logger(__name__).bind(
    component="icechunk",
    site="Rosalia",
    receiver="canopy_01"
)
```

### Best Practices

✅ **DO:**
```python
# Use structured data
log.info("file_processed", file=fname, rows=1000)

# Use clear event names
log.info("rinex_preprocessing_complete")

# Include units in field names
log.info("operation_complete", duration_seconds=1.5, size_mb=10)

# Provide examples for lists
log.debug("sids_found", count=321, examples=sids[:5])
```

❌ **DON'T:**
```python
# Don't use string formatting
log.info(f"Processed {file} in {duration}s")  # Not structured!

# Don't use positional args
log.info("Processed file", fname)  # Won't be structured

# Don't use vague event names
log.info("done")  # Too generic

# Don't include full lists
log.debug("sids_found", all_sids=sids)  # Too verbose for 321 items
```

---

## Filters

### Built-in Filters

#### ErrorFilter
Routes ERROR+ logs to `errors.log`

```python
# Automatically applied to errors.log handler
class ErrorFilter(logging.Filter):
    def filter(self, record):
        return record.levelno >= logging.ERROR
```

#### PerformanceFilter
Routes timing metrics to `performance.json`

```python
# Checks for performance-related fields
class PerformanceFilter(logging.Filter):
    def filter(self, record):
        if hasattr(record, "msg") and isinstance(record.msg, dict):
            return any(key in record.msg for key in [
                "duration_seconds",
                "throughput_files_per_sec",
                "size_mb",
                ...
            ])
```

#### ComponentFilter
Routes by `component` field

```python
# Example: Routes to processor.log
class ComponentFilter(logging.Filter):
    def __init__(self, component_name: str):
        self.component_name = component_name
    
    def filter(self, record):
        if hasattr(record, "msg") and isinstance(record.msg, dict):
            return record.msg.get("component") == self.component_name
```

### Custom Filters

```python
# Filter by site
class SiteFilter(logging.Filter):
    def __init__(self, site_name: str):
        self.site_name = site_name
    
    def filter(self, record):
        if hasattr(record, "msg") and isinstance(record.msg, dict):
            return record.msg.get("site") == self.site_name

# Add to handler
handler.addFilter(SiteFilter("Rosalia"))
```

---

## Log Rotation

### Strategy

| **Handler** | **Rotation** | **Retention** | **Reason** |
|------------|-------------|--------------|-----------|
| Human main | Daily (midnight) | 30 days | Long-term review |
| Errors | Size (50MB) | 5 backups | Error history |
| Machine full | Size (100MB) | 10 backups | Heavy DEBUG output |
| Performance | Size (50MB) | 10 backups | Trend analysis |
| Components | Daily (midnight) | 7 days | Short-term debugging |

### Manual Rotation

```bash
# Force rotation (if needed)
find canvodpy/.logs -name "*.log" -size +100M -exec mv {} {}.old \;

# Clean old archives
find canvodpy/.logs/archive -mtime +30 -delete

# Compress logs
gzip canvodpy/.logs/archive/*.log
```

### Disk Space Management

```bash
# Check sizes
du -sh canvodpy/.logs/*

# Clean specific component
rm -rf canvodpy/.logs/component/processor.log.*

# Keep only last 3 days
find canvodpy/.logs/component -name "*.log.*" -mtime +3 -delete
```

---

## Troubleshooting

### No Logs Appearing

```bash
# 1. Check directory exists
ls -la canvodpy/.logs/

# 2. Check permissions
chmod -R u+w canvodpy/.logs/

# 3. Test logging
python -c "from canvodpy.logging import get_logger; \
           log = get_logger('test'); \
           log.info('test_message', value=123)"

# 4. Check log files
ls -lh canvodpy/.logs/human/main.log
tail canvodpy/.logs/human/main.log
```

### Logs Not in Component File

Component logs require `component` binding:

```python
# Wrong - goes to main.log only
log = get_logger(__name__)
log.info("event")

# Correct - goes to processor.log and main.log
log = get_logger(__name__).bind(component="processor")
log.info("event")
```

### JSON Logs Malformed

```bash
# Check for syntax errors
jq . canvodpy/.logs/machine/full.json >/dev/null

# If errors, find bad lines
grep -n "^[^{]" canvodpy/.logs/machine/full.json

# Each line must be valid JSON
# Not a JSON array - each line is separate
```

### Performance Issues

```bash
# Reduce log verbosity
export CANVODPY_LOG_LEVEL=INFO

# Disable DEBUG logs
# Edit logging_config.py, change DEBUG → INFO for handlers

# Use async logging (advanced)
# Requires custom handler configuration
```

---

## Advanced Topics

### Centralized Logging

Ship logs to Elasticsearch, Loki, or similar:

```bash
# Option 1: Filebeat → Elasticsearch
# Install filebeat, configure to watch .logs/machine/full.json

# Option 2: Promtail → Loki
# Install promtail, configure to scrape .logs/

# Option 3: Fluentd → Multiple destinations
# Install fluentd, configure JSON parser
```

### Log Sampling

For high-volume scenarios, sample logs:

```python
import random

# Log every 10th event
if random.random() < 0.1:
    log.debug("processing_file", file=fname)

# Or use structured sampling
if idx % 10 == 0:
    log.debug("processing_progress", processed=idx, total=total)
```

### Custom Renderers

Create custom output formats:

```python
import structlog

def custom_renderer(logger, name, event_dict):
    # Custom format: CSV
    return f"{event_dict['timestamp']},{event_dict['level']},{event_dict['event']}"

# Add to processor chain
structlog.configure(
    processors=[
        ...
        custom_renderer,
    ]
)
```

---

## Examples

### Debug Failed Processing

```bash
# 1. Find errors
jq 'select(.level == "error")' canvodpy/.logs/machine/full.json

# 2. Get failed file name
jq 'select(.event == "rinex_processing_failed") | .file' \
    canvodpy/.logs/machine/full.json

# 3. Get full context for that file
jq 'select(.file == "ract220.25o")' \
    canvodpy/.logs/component/processor.log

# 4. Check timing before failure
jq 'select(.file == "ract220.25o") 
    | select(.event | contains("start") or contains("complete"))' \
    canvodpy/.logs/machine/full.json
```

### Analyze Performance

```bash
# Average processing time per file
jq -s 'map(select(.event == "rinex_preprocessing_complete")) 
       | map(.duration_seconds) 
       | add / length' \
    canvodpy/.logs/machine/performance.json

# Find slowest 10 files
jq -s 'map(select(.event == "rinex_preprocessing_complete")) 
       | sort_by(.duration_seconds) 
       | reverse 
       | .[0:10] 
       | map({file, duration_seconds})' \
    canvodpy/.logs/machine/performance.json

# Icechunk throughput over time
jq 'select(.event == "batch_write_complete") 
    | {timestamp, receiver, throughput_files_per_sec}' \
    canvodpy/.logs/machine/performance.json
```

### Daily Report

```bash
#!/bin/bash
# daily_log_report.sh

LOG_DIR="canvodpy/.logs"

echo "=== Daily Log Report ==="
echo "Date: $(date)"
echo ""

echo "Errors:"
jq -s 'map(select(.level == "error")) | length' \
    $LOG_DIR/machine/full.json

echo ""
echo "Files Processed:"
jq -s 'map(select(.event == "rinex_preprocessing_complete")) | length' \
    $LOG_DIR/machine/full.json

echo ""
echo "Average Processing Time:"
jq -s 'map(select(.event == "rinex_preprocessing_complete") 
         | .duration_seconds) 
       | add / length' \
    $LOG_DIR/machine/performance.json

echo ""
echo "Icechunk Operations:"
jq -s 'map(select(.component == "icechunk")) | length' \
    $LOG_DIR/machine/full.json
```

---

## See Also

- [Observability Overview](observability.md) - High-level guide
- [Telemetry Guide](telemetry.md) - OpenTelemetry monitoring
- [structlog Documentation](https://www.structlog.org/) - Upstream docs
