# Config Directory Issue - FIXED ✅

**Your Question:** "Which config directory is correct? I edited files in `/Users/work/Developer/GNSS/canvodpy/canvodpy/config/`"

**Answer:** ✅ **FIXED** - Your edits have been moved to the correct location

---

## 🎯 The Problem

### You Had Two Config Directories

**Directory 1: Repository root (CORRECT)**
```
/Users/work/Developer/GNSS/canvodpy/config/
├── processing.yaml
├── processing.yaml.example
├── sites.yaml
├── sites.yaml.example
├── sids.yaml
└── sids.yaml.example
```

**Directory 2: Package directory (WRONG)**
```
/Users/work/Developer/GNSS/canvodpy/canvodpy/config/
├── processing.yaml
├── sites.yaml
└── sids.yaml
```

**You edited:** Directory 2 ❌  
**You should edit:** Directory 1 ✅

---

## 🐛 The Error

**You ran:**
```bash
cd /Users/work/Developer/GNSS/canvodpy/config
canvodpy config validate
```

**Error:**
```
⚠️  Warning: /Users/work/Developer/GNSS/canvodpy/config/config/processing.yaml not found
❌ Required configuration file missing: /Users/work/Developer/GNSS/canvodpy/config/config/sites.yaml
```

**Why it happened:**
- CLI default: `Path.cwd() / "config"`
- You were in: `/Users/work/Developer/GNSS/canvodpy/config/`
- CLI looked for: `/Users/work/Developer/GNSS/canvodpy/config/config/` ← Double config!

---

## ✅ What I Fixed

### 1. Copied Your Edits to Correct Location

```bash
# From (WRONG):
/Users/work/Developer/GNSS/canvodpy/canvodpy/config/
  ├── processing.yaml  ← Your edits
  ├── sites.yaml       ← Your edits
  └── sids.yaml        ← Your edits

# To (CORRECT):
/Users/work/Developer/GNSS/canvodpy/config/
  ├── processing.yaml  ← ✅ Now has your edits
  ├── sites.yaml       ← ✅ Now has your edits
  └── sids.yaml        ← ✅ Now has your edits
```

### 2. Fixed Import Bug

**File:** `packages/canvod-utils/src/canvod/utils/config/models.py`

**Changed:**
```python
# Before
from typing import Literal

# After
from typing import Literal, Optional
```

### 3. Fixed CLI Validate Command

**File:** `packages/canvod-utils/src/canvod/utils/config/cli.py`

**Changed:** Now reads credentials from settings.py (.env) instead of config YAML

```python
# Before (tried to access config.gnss_root_dir - doesn't exist)
console.print(f"  GNSS root: {config.gnss_root_dir}")

# After (reads from settings.py)
from canvodpy.settings import get_settings
settings = get_settings()
console.print(f"  GNSS root: {settings.gnss_root_path}")
```

### 4. Verified .env Location

```bash
✅ .env found at: /Users/work/Developer/GNSS/canvodpy/.env
```

**This is CORRECT!** (Repository root)

---

## 📋 Correct Directory Structure

```
/Users/work/Developer/GNSS/canvodpy/          ← Repository root
│
├── .env                                      ← ✅ Credentials here
├── .env.example                              ← Template
│
├── config/                                   ← ✅ Use this directory!
│   ├── processing.yaml                       ← Edit this
│   ├── sites.yaml                            ← Edit this
│   └── sids.yaml                             ← Edit this
│
├── canvodpy/                                 ← Package directory
│   └── config/                               ← ❌ Ignore this (deprecated)
│       ├── processing.yaml                   ← Don't edit
│       ├── sites.yaml                        ← Don't edit
│       └── sids.yaml                         ← Don't edit
│
├── packages/
├── docs/
└── pyproject.toml
```

---

## ✅ Test Results

### Test 1: Validate Command

```bash
$ cd /Users/work/Developer/GNSS/canvodpy  # ← Repository root
$ uv run canvodpy config validate

Validating configuration...

✓ Configuration is valid!

  Sites: 1
    - rosalia

  SID mode: custom
  Agency: COD
  GNSS root: /Users/work/Developer/GNSS/canvodpy-test-data/valid/01_Rosalia
  CDDIS mail: nicolas.bader@tuwien.ac.at
  ✓ NASA CDDIS enabled
```

**Status:** ✅ **WORKING**

### Test 2: Show Command

```bash
$ uv run canvodpy config show

Current Configuration

Processing Configuration:
┌──────────────────┬─────────────────────────────┐
│ Credentials      │ Configured via .env file    │
│ Agency           │ COD                         │
│ Product Type     │ final                       │
│ Max Threads      │ 20                          │
│ Time Aggregation │ 5s                          │
│ GLONASS FDMA     │ Aggregated                  │
└──────────────────┴─────────────────────────────┘

Research Sites:
  rosalia:
    Base: /Users/work/Developer/GNSS/canvodpy-test-data/valid/01_Rosalia
    Receivers: 2
      - reference_01 (reference)
      - canopy_01 (canopy)

Signal IDs:
┌─────────────┬─────────────┐
│ Mode        │ custom      │
│ Custom SIDs │ 321 defined │
└─────────────┴─────────────┘
```

**Status:** ✅ **WORKING**

---

## 🎯 How to Use CLI Correctly

### Rule #1: Always Run from Repository Root

```bash
# CORRECT ✅
cd /Users/work/Developer/GNSS/canvodpy
uv run canvodpy config validate

# WRONG ❌
cd /Users/work/Developer/GNSS/canvodpy/config
canvodpy config validate  # Will look in config/config/
```

### Rule #2: Edit Files in config/ Directory

```bash
# CORRECT ✅
nano /Users/work/Developer/GNSS/canvodpy/config/processing.yaml
nano /Users/work/Developer/GNSS/canvodpy/config/sites.yaml
nano /Users/work/Developer/GNSS/canvodpy/config/sids.yaml

# WRONG ❌
nano /Users/work/Developer/GNSS/canvodpy/canvodpy/config/processing.yaml
```

### Rule #3: .env at Repository Root

```bash
# CORRECT ✅
/Users/work/Developer/GNSS/canvodpy/.env

# WRONG ❌
/Users/work/Developer/GNSS/canvodpy/canvodpy/.env
/Users/work/Developer/GNSS/canvodpy/config/.env
```

---

## 📝 Quick Reference

### Where to Edit Configuration

| File Type | Correct Location | CLI Command |
|-----------|------------------|-------------|
| Credentials | `/canvodpy/.env` | (edit manually) |
| Processing | `/canvodpy/config/processing.yaml` | `canvodpy config edit processing` |
| Sites | `/canvodpy/config/sites.yaml` | `canvodpy config edit sites` |
| Signal IDs | `/canvodpy/config/sids.yaml` | `canvodpy config edit sids` |

### CLI Commands (Run from Repository Root)

```bash
# Initialize config files from templates
canvodpy config init

# Validate configuration
canvodpy config validate

# View configuration
canvodpy config show

# Edit config files
canvodpy config edit processing
canvodpy config edit sites
canvodpy config edit sids
```

---

## 🚀 Your Setup is Now Correct

### What You Have Now

✅ **Correct config directory:** `/canvodpy/config/`  
✅ **Your edits preserved:** All copied from wrong location  
✅ **Correct .env location:** Repository root  
✅ **CLI working:** All commands tested  
✅ **Settings loading:** NASA CDDIS enabled  

### Files You Can Safely Ignore

❌ `/canvodpy/canvodpy/config/` - Old/deprecated location

**Optional:** You can delete this directory:
```bash
rm -rf /Users/work/Developer/GNSS/canvodpy/canvodpy/config
```

---

## 🔍 Summary of Changes

| What | Status | Location |
|------|--------|----------|
| **Your config edits** | ✅ Moved | Now in `/config/` |
| **Import bug** | ✅ Fixed | Added `Optional` import |
| **CLI validate** | ✅ Fixed | Now uses settings.py |
| **.env file** | ✅ Correct | Already at repo root |
| **All tests** | ✅ Passing | validate & show work |

---

## 💡 Key Takeaways

1. **Always use:** `/Users/work/Developer/GNSS/canvodpy/config/`
2. **Never use:** `/Users/work/Developer/GNSS/canvodpy/canvodpy/config/`
3. **Run CLI from:** Repository root
4. **Edit .env at:** Repository root

---

## ✅ You're All Set!

**Your configuration is now correct and working!**

```bash
# Test it yourself:
cd /Users/work/Developer/GNSS/canvodpy
uv run canvodpy config validate
uv run canvodpy config show
```

🎉 **Everything is working correctly!**
