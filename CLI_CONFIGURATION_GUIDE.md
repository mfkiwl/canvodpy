# 🎯 Configuration CLI Guide - From Scratch

**Command:** `canvodpy config`  
**Purpose:** Manage configuration files for canvodpy

---

## 📋 Quick Reference

```bash
# Show all commands
canvodpy config --help

# Initialize config files
canvodpy config init

# View current config
canvodpy config show

# Validate config
canvodpy config validate

# Edit config files
canvodpy config edit processing
canvodpy config edit sites
canvodpy config edit sids
```

---

## 🚀 Getting Started from Scratch

### Step 1: Check Available Commands

```bash
$ uv run canvodpy --help
```

**Output:**
```
Usage: canvodpy [OPTIONS] COMMAND [ARGS]...

canvodpy CLI tools

╭─ Commands ───────────────────────────────────────╮
│ config   Configuration management                │
╰──────────────────────────────────────────────────╯
```

---

### Step 2: View Config Commands

```bash
$ uv run canvodpy config --help
```

**Output:**
```
Usage: canvodpy config [OPTIONS] COMMAND [ARGS]...

Configuration management

╭─ Commands ───────────────────────────────────────╮
│ init       Initialize configuration files        │
│ validate   Validate configuration files          │
│ show       Display current configuration         │
│ edit       Open configuration file in editor     │
╰──────────────────────────────────────────────────╯
```

---

### Step 3: Initialize Configuration

```bash
$ uv run canvodpy config init
```

**What it does:**
- Creates `config/` directory
- Copies template files:
  - `processing.yaml` (from `processing.yaml.example`)
  - `sites.yaml` (from `sites.yaml.example`)
  - `sids.yaml` (from `sids.yaml.example`)

**Output:**
```
Initializing canvodpy configuration...

✓ Created:
  config/processing.yaml
  config/sites.yaml
  config/sids.yaml

Next steps:
  1. Edit config/processing.yaml:
     - Set gnss_root_dir to your data directory
     - Set cddis_mail (optional, for NASA CDDIS)
  2. Edit config/sites.yaml with your research sites
  3. Run: canvodpy config validate
```

**Note:** If files already exist, use `--force` to overwrite:
```bash
uv run canvodpy config init --force
```

---

### Step 4: Configure Credentials (.env)

**IMPORTANT:** Credentials are NOT in processing.yaml anymore!

**Create .env file:**
```bash
$ cp .env.example .env
$ nano .env  # or your preferred editor
```

**Edit .env:**
```bash
# NASA CDDIS authentication (optional)
CDDIS_MAIL=your.email@example.com

# GNSS data root directory (required)
GNSS_ROOT_DIR=/path/to/your/gnss/data
```

---

### Step 5: Edit Processing Config

```bash
$ uv run canvodpy config edit processing
```

**Opens:** `config/processing.yaml` in your editor ($EDITOR or nano)

**What to configure:**
```yaml
metadata:
  author: Your Name                    # ← Edit this
  email: your.email@example.com        # ← Edit this
  institution: Your Institution        # ← Edit this

aux_data:
  agency: COD                          # Analysis center
  product_type: final                  # final/rapid/ultra-rapid

processing:
  time_aggregation_seconds: 15         # Aggregation interval
  n_max_threads: 20                    # Parallel workers
  keep_rnx_vars:
    - SNR                              # Variables to keep

storage:
  stores_root_dir: /path/to/stores    # ← Edit this!
```

**Key fields to edit:**
- `metadata.author`
- `metadata.email`
- `metadata.institution`
- `storage.stores_root_dir` (where processed data is stored)

---

### Step 6: Edit Sites Config

```bash
$ uv run canvodpy config edit sites
```

**Opens:** `config/sites.yaml`

**Example configuration:**
```yaml
sites:
  rosalia:
    base_dir: /data/gnss/01_Rosalia
    receivers:
      reference_01:
        directory: 01_reference_01
        type: reference
        antenna_height: 2.0
      
      canopy_01:
        directory: 02_canopy_01
        type: canopy
        antenna_height: 15.0
    
    vod_analyses:
      pair_01:
        canopy_receiver: canopy_01
        reference_receiver: reference_01
        canopy_height: 15.0
```

**What to configure:**
- Site name(s)
- Base directory path
- Receiver names and directories
- Receiver types (reference/canopy)
- Analysis pairs

---

### Step 7: Edit Signal IDs Config (Optional)

```bash
$ uv run canvodpy config edit sids
```

**Opens:** `config/sids.yaml`

**Default (use all signals):**
```yaml
mode: all
```

**Custom (specific signals):**
```yaml
mode: custom
custom_sids:
  - G01|L1|C  # GPS L1 C/A
  - G01|L2|W  # GPS L2 P(Y)
  - E01|E1|C  # Galileo E1
```

**Preset (predefined set):**
```yaml
mode: preset
preset: gps_galileo
```

---

### Step 8: View Configuration

```bash
$ uv run canvodpy config show
```

**Output:**
```
Current Configuration

Processing Configuration:
┌──────────────────┬─────────────────────────────┐
│ Credentials      │ Configured via .env file    │
│                  │ (CDDIS_MAIL, GNSS_ROOT_DIR) │
│ Agency           │ COD                         │
│ Product Type     │ final                       │
│ Max Threads      │ 20                          │
│ Time Aggregation │ 15s                         │
│ GLONASS FDMA     │ Aggregated                  │
└──────────────────┴─────────────────────────────┘

Research Sites:
  rosalia:
    Base: /path/to/your/gnss/data/01_Rosalia
    Receivers: 2
      - reference_01 (reference)
      - canopy_01 (canopy)

Signal IDs:
┌──────┬─────┐
│ Mode │ all │
└──────┴─────┘
```

**View specific section:**
```bash
uv run canvodpy config show --section processing
uv run canvodpy config show --section sites
uv run canvodpy config show --section sids
```

---

### Step 9: Validate Configuration

```bash
$ uv run canvodpy config validate
```

**Success:**
```
Validating configuration...

✓ Configuration is valid!

  Sites: 1
    - rosalia

  SID mode: all
  Agency: COD
  GNSS root: /path/to/your/gnss/data

  ✓ NASA CDDIS enabled
```

**Failure:**
```
❌ Validation failed:

Field required: stores_root_dir
```

---

## 📁 File Structure After Init

```
your-project/
├── .env                          ← Create this manually
│   ├── CDDIS_MAIL=...           
│   └── GNSS_ROOT_DIR=...
│
└── config/                       ← Created by `config init`
    ├── processing.yaml           ← Processing settings
    ├── sites.yaml                ← Site definitions
    └── sids.yaml                 ← Signal ID configuration
```

---

## 🔧 CLI Options

### Custom Config Directory

```bash
# Use different config directory
uv run canvodpy config init --config-dir /path/to/config
uv run canvodpy config show --config-dir /path/to/config
uv run canvodpy config validate --config-dir /path/to/config
```

### Force Overwrite

```bash
# Overwrite existing config files
uv run canvodpy config init --force
```

---

## 📝 Complete Workflow Example

```bash
# 1. Initialize config
cd /path/to/your/project
uv run canvodpy config init

# 2. Create .env file
cp .env.example .env
nano .env
# Set: CDDIS_MAIL, GNSS_ROOT_DIR

# 3. Edit processing config
uv run canvodpy config edit processing
# Update: author, email, institution, stores_root_dir

# 4. Edit sites config
uv run canvodpy config edit sites
# Configure: your research sites

# 5. View configuration
uv run canvodpy config show

# 6. Validate
uv run canvodpy config validate

# 7. Start using canvodpy!
```

---

## 🎯 Key Points

### Two Configuration Systems

**1. Settings (Credentials) → .env file**
```bash
CDDIS_MAIL=your@email.com
GNSS_ROOT_DIR=/data/gnss
```

**Used for:**
- NASA CDDIS FTP authentication (optional)
- Data directory paths

---

**2. Configuration (Settings) → YAML files**
```yaml
# processing.yaml
metadata: ...
aux_data: ...
processing: ...

# sites.yaml
sites: ...

# sids.yaml
mode: all
```

**Used for:**
- Processing parameters
- Site definitions
- Signal ID configuration
- Metadata

---

### When to Use Each Command

| Command | When to Use |
|---------|-------------|
| `init` | First time setup, create config files |
| `show` | View current configuration |
| `validate` | Check config is correct before processing |
| `edit` | Modify configuration settings |

---

## 🐛 Troubleshooting

### Issue: Command not found

```bash
$ canvodpy config init
zsh: command not found: canvodpy
```

**Solution:** Use `uv run`
```bash
uv run canvodpy config init
```

---

### Issue: Template not found

```
❌ Template directory not found: /path/to/templates
```

**Solution:** Run from repository root
```bash
cd /path/to/canvodpy  # Repository root
uv run canvodpy config init
```

---

### Issue: Config files already exist

```
⊘ Skipped (already exist):
  config/processing.yaml
```

**Solution:** Use `--force` to overwrite
```bash
uv run canvodpy config init --force
```

---

### Issue: Validation fails

```
❌ Validation failed: Field required: stores_root_dir
```

**Solution:** Edit the config file
```bash
uv run canvodpy config edit processing
# Set stores_root_dir
```

---

## 📚 Additional Resources

**Files created by CLI:**
- `config/processing.yaml` - Processing parameters
- `config/sites.yaml` - Research site definitions
- `config/sids.yaml` - Signal ID configuration

**Manual files (you create):**
- `.env` - Credentials (copy from `.env.example`)

**Template files (in repository):**
- `config/processing.yaml.example`
- `config/sites.yaml.example`
- `config/sids.yaml.example`
- `.env.example`

---

## ✅ Summary

**To start from scratch:**

1. **`uv run canvodpy config init`** - Create config files
2. **`cp .env.example .env`** - Create credentials file
3. **Edit .env** - Set CDDIS_MAIL, GNSS_ROOT_DIR
4. **`uv run canvodpy config edit processing`** - Configure settings
5. **`uv run canvodpy config edit sites`** - Define sites
6. **`uv run canvodpy config show`** - Review configuration
7. **`uv run canvodpy config validate`** - Check it's correct
8. **Start processing!**

---

**Ready to configure canvodpy!** 🚀
