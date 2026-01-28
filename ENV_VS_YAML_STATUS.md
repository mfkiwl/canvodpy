# Configuration Status: .env vs processing.yaml

**Date:** 2026-01-25  
**Question:** Is the .env issue resolved in favor of user config YAML?

---

## 📊 Current State

### ✅ Partially Resolved

**What's Fixed:**
1. ✅ Duplicate credential fields **removed** from processing.yaml
2. ✅ processing.yaml now has comments directing users to .env
3. ✅ ProcessingConfig has credentials marked as **DEPRECATED**

**What's NOT Changed:**
- ⚠️ settings.py **still loads from .env** (not from YAML)
- ⚠️ Two separate systems still exist

---

## 🏗️ Current Architecture

### System 1: Credentials via .env (settings.py)

**File:** `canvodpy/src/canvodpy/settings.py`

```python
# Loads from .env file
class AppSettings:
    def __init__(self):
        self.cddis_mail = os.getenv('CDDIS_MAIL')
        self.gnss_root_dir = os.getenv('GNSS_ROOT_DIR')
```

**Used by:**
- `canvodpy/orchestrator/processor.py`
- `canvod-aux/pipeline.py`

**Status:** ✅ **ACTIVE** - Currently used for FTP authentication

---

### System 2: Processing Config via YAML (config loader)

**File:** `canvodpy/config/processing.yaml`

```yaml
# No credentials here anymore (removed)
metadata:
  author: Your Name
  email: your.email@example.com

aux_data:
  agency: COD
  product_type: final

processing:
  time_aggregation_seconds: 15
  keep_rnx_vars: [SNR]
```

**Loader:** `canvod-utils/config/loader.py`

```python
class ProcessingConfig(BaseModel):
    metadata: MetadataConfig
    credentials: Optional[CredentialsConfig] = Field(
        None,
        description="[DEPRECATED] Use .env file for credentials instead"
    )
    # ... other fields
```

**Status:** ⚠️ **NOT USED** for credentials

---

## 📋 What Was Fixed

### processing.yaml Header Comment:
```yaml
# =============================================================================
# Processing Configuration
# =============================================================================
# This file contains processing parameters and settings.
# For credentials (CDDIS_MAIL, GNSS_ROOT_DIR), use .env file instead.
```

### credentials Section Removed:
```yaml
# OLD (removed):
credentials:
  cddis_mail: your.email@example.com  
  gnss_root_dir: /path/to/data

# NEW (not present):
# See .env file for credentials
```

### Model Updated:
```python
credentials: Optional[CredentialsConfig] = Field(
    None,
    description="[DEPRECATED] Use .env file for credentials instead"
)
```

---

## ❓ What You're Asking

**"Is it resolved in favor of user config YAML?"**

**Answer:** ⚠️ **NO - It's resolved in favor of .env file**

### Current Design:
- **Credentials:** .env file (via settings.py)
- **Processing settings:** processing.yaml (via config loader)

### This is NOT using YAML for credentials

---

## 🤔 What Do You Want?

### Option A: Keep Current (Credentials in .env) ✅ **IMPLEMENTED**

**Pros:**
- ✅ Python ecosystem standard (.env for credentials)
- ✅ Security (.env excluded from git by default)
- ✅ Simple separation (credentials vs settings)
- ✅ Already working

**Cons:**
- ⚠️ Two configuration files
- ⚠️ Slightly more complex for users

**Status:** This is the CURRENT state

---

### Option B: Migrate to YAML-Only (Your Question?) ❓

**Move credentials TO processing.yaml**

**Changes needed:**
1. Un-deprecate `credentials` field in ProcessingConfig
2. Modify settings.py to load from processing.yaml instead of .env
3. Update documentation
4. Create migration guide

**Pros:**
- ✅ Single configuration file
- ✅ All settings in one place
- ✅ YAML is more structured

**Cons:**
- ⚠️ Less secure (easier to commit credentials to git)
- ⚠️ Not Python ecosystem standard
- ⚠️ Would break existing .env workflows

**Status:** NOT IMPLEMENTED

---

## 🎯 Decision Point

**You need to decide:**

### Keep .env (Current) ✅
```yaml
# .env
CDDIS_MAIL=your@email.com
GNSS_ROOT_DIR=/path/to/data

# processing.yaml (no credentials)
metadata:
  author: Your Name
aux_data:
  agency: COD
```

**Recommendation:** ✅ **Keep this** - it's the standard approach

---

### Migrate to YAML-only
```yaml
# processing.yaml (with credentials)
credentials:
  cddis_mail: your@email.com
  gnss_root_dir: /path/to/data

metadata:
  author: Your Name
aux_data:
  agency: COD
```

**Recommendation:** ⚠️ **Not recommended** - less secure, non-standard

---

## 📝 My Recommendation

**Keep the current design (.env for credentials)**

**Reasons:**
1. **Security:** .env is .gitignored by default
2. **Standard:** Python ecosystem convention
3. **Clean separation:** Credentials vs configuration
4. **Already implemented:** Working correctly
5. **Environment-specific:** Easy to swap for dev/staging/prod

---

## 🔧 If You Want YAML-Only (Implementation)

If you REALLY want to migrate to YAML-only:

### Step 1: Update ProcessingConfig
```python
# In canvod-utils/config/models.py
class ProcessingConfig(BaseModel):
    metadata: MetadataConfig
    credentials: CredentialsConfig  # Make required, not Optional
    aux_data: AuxDataConfig
    # ...
```

### Step 2: Update settings.py
```python
# In canvodpy/settings.py
from canvod.utils.config import load_config

def get_settings() -> AppSettings:
    config = load_config()
    return AppSettings(
        cddis_mail=config.processing.credentials.cddis_mail,
        gnss_root_dir=config.processing.credentials.gnss_root_dir
    )
```

### Step 3: Update processing.yaml
```yaml
credentials:
  cddis_mail: your@email.com
  gnss_root_dir: /path/to/data
```

### Step 4: Remove .env support
```python
# Remove python-dotenv dependency
# Remove load_dotenv() calls
```

**Effort:** ~1-2 hours  
**Risk:** Medium (could break existing workflows)

---

## ✅ Summary

| Aspect | Current State | Your Question |
|--------|--------------|---------------|
| **Credentials location** | .env file | You asked about YAML |
| **Status** | ✅ Working | Not migrated to YAML |
| **Duplication** | ✅ Removed | Fixed |
| **Standard practice** | ✅ Follows Python conventions | Would break conventions |
| **Recommendation** | ✅ Keep as-is | Don't migrate |

---

## 🎯 Answer to Your Question

**"Is the .env issue resolved in favor of the user config YAML?"**

### Short Answer: ⚠️ NO

**Resolution:** ✅ In favor of **.env file** (not YAML)

**What was fixed:**
- ✅ Duplicate fields removed from YAML
- ✅ Clear separation: .env for credentials, YAML for settings
- ✅ Documentation added

**What you seem to want:**
- ❓ Use YAML for credentials instead of .env

**My recommendation:**
- ✅ **Keep .env** - it's more secure and standard
- ❌ **Don't migrate to YAML** - less secure, non-standard

---

**Do you want to:**
1. ✅ Keep current design (.env for credentials) - RECOMMENDED
2. ❓ Migrate to YAML-only (I can implement this if you insist)

Let me know!
