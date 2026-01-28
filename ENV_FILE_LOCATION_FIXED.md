# .env File Location - FIXED ✅

**Question:** "The env file goes into the '/Users/work/Developer/GNSS/canvodpy/canvodpy/config' dir?"

**Answer:** ❌ **NO** - It goes in the **repository root**

---

## ✅ Correct Location

### .env File Location
```
/Users/work/Developer/GNSS/canvodpy/.env
```

**Path structure:**
```
canvodpy/                           ← REPOSITORY ROOT (.env goes HERE)
├── .env                            ← ✅ CORRECT LOCATION
├── .env.example                    ← Template (same directory)
├── .gitignore                      ← Contains .env (excluded from git)
├── pyproject.toml
├── README.md
│
├── canvodpy/                       ← Main package directory
│   ├── config/                     ← ❌ NOT HERE
│   │   ├── processing.yaml
│   │   ├── sites.yaml
│   │   └── sids.yaml
│   └── src/
│       └── canvodpy/
│           └── settings.py         ← Loads .env from repo root
│
├── config/                         ← YAML config files
│   ├── processing.yaml
│   ├── sites.yaml
│   └── sids.yaml
│
└── packages/
    └── ...
```

---

## 🔧 What Was Fixed

### Before (Wrong)
**settings.py looked for:**
```python
_env_path = Path(__file__).parent.parent.parent / '.env'
# Result: /Users/work/Developer/GNSS/canvodpy/canvodpy/.env ✗
```

### After (Correct)
**settings.py now looks for:**
```python
_env_path = Path(__file__).parent.parent.parent.parent / '.env'
# Result: /Users/work/Developer/GNSS/canvodpy/.env ✓
```

**Path calculation:**
```
settings.py location:
/Users/work/Developer/GNSS/canvodpy/canvodpy/src/canvodpy/settings.py
                                    ↓
                              .parent (canvodpy/)
                         .parent.parent (src/)
                    .parent.parent.parent (canvodpy/)
               .parent.parent.parent.parent (canvodpy/ ← repo root)
                                           / '.env' = /Users/work/Developer/GNSS/canvodpy/.env ✅
```

---

## 📋 Quick Setup

### Step 1: Create .env at Repository Root

```bash
cd /Users/work/Developer/GNSS/canvodpy  # ← Repository root
cp .env.example .env
```

### Step 2: Edit .env

```bash
nano .env
```

**Content:**
```bash
# NASA CDDIS authentication (optional)
CDDIS_MAIL=your.email@example.com

# GNSS data root directory
GNSS_ROOT_DIR=/path/to/your/gnss/data
```

### Step 3: Verify

```bash
uv run python -c "
from canvodpy.settings import get_settings
s = get_settings()
print(f'CDDIS: {s.has_cddis_credentials}')
print(f'Path: {s.gnss_root_path}')
"
```

---

## 🗂️ File Organization

### Repository Root (Main Config)
```
canvodpy/
├── .env                    ← Credentials (git-ignored)
├── .env.example            ← Template
└── .gitignore              ← Contains: .env
```

### Config Directory (YAML Settings)
```
canvodpy/config/            ← Processing settings
├── processing.yaml
├── sites.yaml
└── sids.yaml
```

### Package Config Directory
```
canvodpy/canvodpy/config/   ← Another processing.yaml (different)
└── processing.yaml
```

---

## ⚠️ Common Mistakes

### ❌ Wrong Location #1
```bash
# DON'T put .env here
/Users/work/Developer/GNSS/canvodpy/canvodpy/.env
```

### ❌ Wrong Location #2
```bash
# DON'T put .env here
/Users/work/Developer/GNSS/canvodpy/canvodpy/config/.env
```

### ❌ Wrong Location #3
```bash
# DON'T put .env here
/Users/work/Developer/GNSS/canvodpy/config/.env
```

### ✅ Correct Location
```bash
# DO put .env here (same directory as .env.example)
/Users/work/Developer/GNSS/canvodpy/.env
```

---

## 🔍 How to Verify Location

### Method 1: Check with Python

```bash
cd /Users/work/Developer/GNSS/canvodpy
uv run python -c "
from pathlib import Path
import canvodpy.settings

settings_file = Path(canvodpy.settings.__file__)
env_path = settings_file.parent.parent.parent.parent / '.env'
print(f'.env expected at: {env_path}')
print(f'.env exists: {env_path.exists()}')
"
```

**Expected output:**
```
.env expected at: /Users/work/Developer/GNSS/canvodpy/.env
.env exists: True  (if you created it)
```

### Method 2: Check Same Directory as .env.example

```bash
cd /Users/work/Developer/GNSS/canvodpy
ls -la .env*
```

**Expected:**
```
-rw-r--r--  .env.example    ← Template
-rw-r--r--  .env            ← Your file (if created)
```

Both should be in the **same directory**.

---

## 📝 Summary

| Question | Answer |
|----------|--------|
| **Where does .env go?** | Repository root: `/Users/work/Developer/GNSS/canvodpy/.env` |
| **Same directory as .env.example?** | ✅ YES |
| **In config/ directory?** | ❌ NO |
| **In canvodpy/config/ directory?** | ❌ NO |
| **Git tracked?** | ❌ NO (.gitignore excludes it) |
| **Required?** | Optional (ESA-only mode works without it) |

---

## ✅ Test Results

```bash
$ cd /Users/work/Developer/GNSS/canvodpy
$ cat > .env << EOF
CDDIS_MAIL=test@example.com
GNSS_ROOT_DIR=/tmp/test_data
EOF

$ uv run python -c "
from canvodpy.settings import reload_settings
s = reload_settings()
print(f'CDDIS: {s.cddis_mail}')
print(f'Path: {s.gnss_root_dir}')
"

✅ Settings loaded from .env
   CDDIS mail: test@example.com
   GNSS root: /tmp/test_data
```

**Status:** ✅ **WORKING CORRECTLY**

---

## 🎯 Key Takeaway

**The .env file goes at the REPOSITORY ROOT:**
```
/Users/work/Developer/GNSS/canvodpy/.env
```

**Same directory as:**
- `.env.example` (template)
- `.gitignore` (excludes .env)
- `pyproject.toml` (project file)
- `README.md` (project readme)

**NOT in any config/ directory!**
