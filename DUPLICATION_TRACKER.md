# Code Duplication Tracker

## Purpose
Tracks intentionally duplicated code across independent packages in the monorepo.
When updating shared utilities, use this to find all copies that need updating.

---

## Duplicated Utilities Registry

### 1. Unit Registry (UREG)

**Canonical Source:** `canvod-aux/src/canvod/aux/_internal/units.py`

**Copies:**
- `canvod-aux/src/canvod/aux/_internal/units.py` ← CANONICAL
- `canvod-readers/src/canvod/readers/_internal/units.py`
- `canvod-vod/src/canvod/vod/_internal/units.py`
- `canvod-viz/src/canvod/viz/_internal/units.py`

**Content:**
```python
import pint

UREG = pint.UnitRegistry()
UREG.define('dB = []')
UREG.define('dBHz = []')
```

**Last Updated:** 2025-01-13

---

### 2. Date/Time Utilities

**Canonical Source:** `canvod-aux/src/canvod/aux/_internal/date_utils.py`

**Copies:**
- `canvod-aux/src/canvod/aux/_internal/date_utils.py` ← CANONICAL
- `canvod-readers/src/canvod/readers/_internal/date_utils.py`
- `canvod-store/src/canvod/store/_internal/date_utils.py`

**Functions:**
- `YYYYDOY` class (from_str, from_date, to_str, date property)
- `get_gps_week_from_filename(filename: Path) -> str`

**Last Updated:** 2025-01-13

---

### 3. Logger Utilities

**Canonical Source:** `canvod-aux/src/canvod/aux/_internal/logger.py`

**Copies:**
- `canvod-aux/src/canvod/aux/_internal/logger.py` ← CANONICAL
- `canvod-readers/src/canvod/readers/_internal/logger.py`
- `canvod-grids/src/canvod/grids/_internal/logger.py`
- `canvod-vod/src/canvod/vod/_internal/logger.py`
- `canvod-store/src/canvod/store/_internal/logger.py`
- `canvod-viz/src/canvod/viz/_internal/logger.py`

**Functions:**
- `get_logger(name: str = None) -> logging.Logger`
- `set_file_context(filename: str) -> None`
- `reset_context() -> None`

**Last Updated:** 2025-01-13

---

## Update Procedure

When modifying a duplicated utility:

1. **Update the canonical source first** (marked with ← CANONICAL above)

2. **Find all copies** using this tracker

3. **Propagate changes** to all copies:
   ```bash
   # Example: Update UREG across all packages
   cp canvod-aux/src/canvod/aux/_internal/units.py \
      canvod-readers/src/canvod/readers/_internal/units.py
   
   cp canvod-aux/src/canvod/aux/_internal/units.py \
      canvod-vod/src/canvod/vod/_internal/units.py
   ```

4. **Update "Last Updated" timestamp** in this tracker

5. **Run tests** across affected packages:
   ```bash
   just test-all
   ```

---

## Sync Helper Script (Optional)

Create `scripts/sync-duplicated-code.sh` to automate propagation:

```bash
#!/bin/bash
# Sync duplicated utilities from canonical sources

set -e

echo "Syncing duplicated utilities..."

# UREG
echo "  → Syncing units.py..."
cp packages/canvod-aux/src/canvod/aux/_internal/units.py \
   packages/canvod-readers/src/canvod/readers/_internal/units.py
cp packages/canvod-aux/src/canvod/aux/_internal/units.py \
   packages/canvod-vod/src/canvod/vod/_internal/units.py

# Date utils
echo "  → Syncing date_utils.py..."
cp packages/canvod-aux/src/canvod/aux/_internal/date_utils.py \
   packages/canvod-readers/src/canvod/readers/_internal/date_utils.py

# Logger
echo "  → Syncing logger.py..."
cp packages/canvod-aux/src/canvod/aux/_internal/logger.py \
   packages/canvod-readers/src/canvod/readers/_internal/logger.py
cp packages/canvod-aux/src/canvod/aux/_internal/logger.py \
   packages/canvod-grids/src/canvod/grids/_internal/logger.py

echo "✓ Sync complete!"
echo "Run 'just test-all' to verify changes"
```

---

## Design Principles

1. **Canonical Source:** Always one package owns the "true" version
2. **Minimal Copies:** Only copy what each package actually needs
3. **Track Everything:** Every duplicated file listed here
4. **Version in Sync:** All copies should be identical (except imports)
5. **Test After Sync:** Always run tests after propagating changes

---

## Why Duplication Over Shared Package?

- ✅ True package independence (can split to separate repos)
- ✅ No cross-package coupling during development
- ✅ Each package can be installed standalone via PyPI
- ✅ Simple utilities (10-30 lines) - duplication cost is low
- ⚠️ Requires discipline to keep copies in sync (this tracker helps!)

---

## Verification

Check for drift between copies:

```bash
# Compare UREG implementations
diff packages/canvod-aux/src/canvod/aux/_internal/units.py \
     packages/canvod-readers/src/canvod/readers/_internal/units.py

# Compare date utils
diff packages/canvod-aux/src/canvod/aux/_internal/date_utils.py \
     packages/canvod-readers/src/canvod/readers/_internal/date_utils.py

# Should show no differences (or only import differences)
```

---

## Future: Consider Consolidation?

If duplication becomes painful (>5 packages, frequent changes):
- Reconsider `canvod-utils` shared package
- But only if maintaining independence isn't critical anymore
- For now, tracked duplication is manageable and keeps packages splittable
