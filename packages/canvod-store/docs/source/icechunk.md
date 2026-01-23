# IceChunk Integration

## What is IceChunk?

IceChunk is a cloud-native transactional storage format for multidimensional array data. It provides:

- **Transactional semantics** - ACID guarantees for data writes
- **Version control** - Built-in versioning like git for data
- **Cloud-native** - S3-compatible object storage
- **Zarr-compatible** - Works with Zarr ecosystem

## Why IceChunk for GNSS VOD?

### Benefits

1. **Time-series optimized** - Efficient chunking for temporal data
2. **Versioning** - Track data processing versions
3. **Incremental updates** - Append new observations efficiently
4. **Cloud-ready** - Deploy to AWS/GCP/Azure
5. **Python integration** - Native xarray support

### Comparison with Alternatives

| Feature | IceChunk | Zarr | NetCDF4 | HDF5 |
|---------|----------|------|---------|------|
| Version control | ✅ | ❌ | ❌ | ❌ |
| Cloud-native | ✅ | ✅ | ❌ | ❌ |
| Transactions | ✅ | ❌ | ❌ | ❌ |
| Chunking | ✅ | ✅ | ✅ | ✅ |
| Compression | ✅ | ✅ | ✅ | ✅ |

## Storage Structure

### Directory Layout

```
stores/
├── rosalia/
│   ├── rinex/              # RINEX observations
│   │   ├── .icechunk/      # IceChunk metadata
│   │   ├── data/           # Chunked data files
│   │   └── versions/       # Version snapshots
│   └── vod/                # VOD results
│       ├── .icechunk/
│       ├── data/
│       └── versions/
```

### Chunk Strategy

**Default chunking for RINEX data:**
```python
{
    "epoch": 34560,  # ~24 hours @ 2.5s sampling
    "sid": -1        # All signals in one chunk
}
```

**Rationale:**
- Epoch chunking aligns with daily processing
- Signal ID (-1) keeps all signals together for efficient VOD calculation
- Typical chunk size: 50-100 MB (optimal for S3)

## Configuration

### Compression Settings

```yaml
# config/processing.yaml
icechunk:
  compression_algorithm: zstd  # zstd, lz4, gzip
  compression_level: 5          # 1-9
  inline_threshold: 512         # bytes
  get_concurrency: 1            # parallel reads
```

### Chunk Strategies

```yaml
chunk_strategies:
  rinex_store:
    epoch: 34560    # 24 hours @ 2.5s
    sid: -1         # All signals
  vod_store:
    epoch: 34560    # Match RINEX
    sid: -1         # All signals
```

## Usage Examples

### Initialize Store

```python
from icechunk import IcechunkStore

store = IcechunkStore.open_or_create(
    storage="file:///path/to/store",
    read_only=False
)
```

### Write with Transaction

```python
with store.transaction() as txn:
    # Prepare dataset
    ds = preprocess_dataset(raw_data)
    
    # Write to store
    ds.to_zarr(store, mode="a")
    
    # Commit transaction
    txn.commit(message="Added 2024-01-15 data")
```

### Read Specific Version

```python
# List versions
versions = store.list_versions()

# Open specific version
store_v1 = IcechunkStore.open(
    storage="file:///path/to/store",
    version=versions[0]
)

ds = xr.open_zarr(store_v1)
```

### Query Time Range

```python
# Open store
ds = xr.open_zarr(store)

# Select time range
subset = ds.sel(
    epoch=slice("2024-01-01", "2024-01-31")
)
```

## Version Control Workflow

### Track Processing Versions

```python
# Process version 1
with store.transaction() as txn:
    ds_v1 = process_algorithm_v1(data)
    ds_v1.to_zarr(store)
    txn.commit(message="Algorithm v1.0")

# Process version 2 (improved algorithm)
with store.transaction() as txn:
    ds_v2 = process_algorithm_v2(data)
    ds_v2.to_zarr(store, mode="w")  # Overwrite
    txn.commit(message="Algorithm v2.0 - improved accuracy")
```

### Compare Versions

```python
# Load both versions
ds_v1 = xr.open_zarr(store, version="v1.0")
ds_v2 = xr.open_zarr(store, version="v2.0")

# Compare results
diff = ds_v2["vod"] - ds_v1["vod"]
print(f"Mean difference: {diff.mean().values}")
```

## Performance Optimization

### Parallel Writing

```python
from dask.distributed import Client

client = Client()

# Write in parallel
ds.to_zarr(
    store,
    compute=True,
    consolidated=True
)
```

### Compression Tuning

**For fast writes (development):**
```python
encoding = {
    "vod": {"compressor": None}  # No compression
}
ds.to_zarr(store, encoding=encoding)
```

**For small storage (production):**
```python
import zarr

encoding = {
    "vod": {
        "compressor": zarr.Blosc(
            cname="zstd",
            clevel=9,
            shuffle=2
        )
    }
}
ds.to_zarr(store, encoding=encoding)
```

## Cloud Deployment

### S3 Backend

```python
store = IcechunkStore.open_or_create(
    storage="s3://bucket-name/path/to/store",
    storage_config={
        "region": "us-east-1",
        "credentials": "auto"
    }
)
```

### Azure Backend

```python
store = IcechunkStore.open_or_create(
    storage="az://container/path/to/store",
    storage_config={
        "account_name": "myaccount",
        "account_key": "..."
    }
)
```

## Troubleshooting

### Store Corruption
```python
# Check store integrity
store.fsck()

# Repair if needed
store.repair()
```

### Version Cleanup
```python
# List old versions
old_versions = store.list_versions()[:-5]  # Keep last 5

# Delete old versions
for v in old_versions:
    store.delete_version(v)
```

## Further Reading

- [IceChunk Documentation](https://icechunk.io)
- [Zarr Tutorial](https://zarr.readthedocs.io)
- [Xarray with Zarr](https://docs.xarray.dev/en/stable/user-guide/io.html#zarr)
