# CLI Tools

## Overview

The `canvodpy` command-line interface provides tools for managing configuration files.

## Installation

CLI tools are available after installing canvod-utils:

```bash
# Install from monorepo root
~/.local/bin/uv sync

# Verify installation
canvodpy --help
```

## Commands

### `config init`

Initialize configuration files by copying templates.

```bash
canvodpy config init
```

**Output:**
```
Initializing configuration files...
✓ Copied config/processing.yaml.example → config/processing.yaml
✓ Copied config/sites.yaml.example → config/sites.yaml
✓ Copied config/sids.yaml.example → config/sids.yaml

Next steps:
1. Edit config/processing.yaml
2. Edit config/sites.yaml
3. Run: canvodpy config validate
```

**Options:**
```bash
# Force overwrite existing files
canvodpy config init --force
```

---

### `config validate`

Validate configuration files.

```bash
canvodpy config validate
```

**Successful validation:**
```
Validating configuration...
✓ Processing configuration is valid
✓ Sites configuration is valid
✓ Signal IDs configuration is valid

Configuration summary:
  Author: Nicolas François Bader
  Email: nicolas.bader@tuwien.ac.at
  GNSS Root: /path/to/gnss/data
  Stores Root: /path/to/stores
  Sites: 2 (rosalia, tuw)
  Agency: COD
  Product: final
```

**Failed validation:**
```
Validating configuration...
❌ Validation failed:

Errors in config/processing.yaml:
  - metadata.email: value is not a valid email address
  - credentials.gnss_root_dir: Path does not exist: /bad/path
  - processing.time_aggregation_seconds: ensure this value is less than or equal to 300

Please fix these errors and try again.
```

---

### `config show`

Display current configuration.

```bash
canvodpy config show
```

**Output (rich formatted tables):**
```
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Setting           ┃ Value                        ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Author            │ Nicolas François Bader             │
│ Email             │ nicolas.bader@tuwien.ac.at   │
│ Institution       │ TU Wien                      │
│ GNSS Root Dir     │ /path/to/gnss/data           │
│ Stores Root Dir   │ /path/to/stores              │
│ Agency            │ COD                          │
│ Product Type      │ final                        │
│ Time Aggregation  │ 15 seconds                   │
└───────────────────┴──────────────────────────────┘
```

**Show specific section:**
```bash
# Show only metadata
canvodpy config show --section metadata

# Show only processing params
canvodpy config show --section processing

# Show only storage settings
canvodpy config show --section storage
```

---

### `config edit`

Open configuration file in your default editor.

```bash
# Edit processing config
canvodpy config edit processing

# Edit sites config
canvodpy config edit sites

# Edit sids config
canvodpy config edit sids
```

**Uses `$EDITOR` environment variable:**
```bash
# Set your preferred editor
export EDITOR=vim
export EDITOR=nano
export EDITOR=code  # VS Code
export EDITOR=subl  # Sublime Text
```

**If `$EDITOR` is not set:**
```
❌ $EDITOR environment variable not set
   Set it with: export EDITOR=vim
   Or edit manually: config/processing.yaml
```

---

## Common Workflows

### Initial Setup

```bash
# 1. Initialize config files
canvodpy config init

# 2. Edit processing settings
canvodpy config edit processing

# Set your metadata, paths, and preferences

# 3. Validate
canvodpy config validate

# 4. Show final config
canvodpy config show
```

### Update Settings

```bash
# Edit settings
canvodpy config edit processing

# Validate changes
canvodpy config validate
```

### Review Configuration

```bash
# Show all settings
canvodpy config show

# Show specific section
canvodpy config show --section metadata
canvodpy config show --section storage
```

### Troubleshooting

```bash
# Check validation errors
canvodpy config validate

# View current settings
canvodpy config show

# Reset to defaults (backup first!)
mv config/processing.yaml config/processing.yaml.backup
canvodpy config init
```

---

## Configuration Sections

### Available Sections for `show`

```bash
canvodpy config show --section <section>
```

**Sections:**
- `metadata` - Author, email, institution
- `credentials` - CDDIS mail, GNSS root directory
- `aux_data` - Agency, product type, FTP settings
- `processing` - Time aggregation, threads, variables
- `compression` - Zlib settings
- `icechunk` - Storage compression and chunking
- `storage` - Store paths and strategies
- `sites` - Research sites configuration
- `sids` - Signal ID selection

---

## Environment Variables

### `CANVOD_CONFIG_DIR`

Override config directory location:

```bash
export CANVOD_CONFIG_DIR=/custom/path/to/config
canvodpy config validate
```

### `EDITOR`

Set your preferred text editor:

```bash
export EDITOR=vim
canvodpy config edit processing
```

---

## Tips & Tricks

### 1. Quick Validation

Add to your shell profile:

```bash
# ~/.zshrc or ~/.bashrc
alias cvv="canvodpy config validate"
```

Usage:
```bash
cvv  # Quick validation
```

### 2. Edit and Validate

```bash
canvodpy config edit processing && canvodpy config validate
```

### 3. Show Summary After Changes

```bash
canvodpy config edit processing && \
canvodpy config validate && \
canvodpy config show
```

### 4. Backup Before Changes

```bash
cp config/processing.yaml config/processing.yaml.backup
canvodpy config edit processing
```

### 5. Diff Changes

```bash
# Before editing
canvodpy config show > before.txt

# After editing
canvodpy config show > after.txt

# View differences
diff before.txt after.txt
```

---

## Exit Codes

Useful for scripting:

```bash
canvodpy config validate
echo $?  # 0 = success, 1 = validation failed

# In scripts
if canvodpy config validate; then
    echo "Config is valid"
    ./run_processing.sh
else
    echo "Config has errors"
    exit 1
fi
```

---

## Examples

### CI/CD Integration

```yaml
# .github/workflows/test.yml
- name: Validate configuration
  run: |
    canvodpy config init
    # Copy test config
    cp tests/fixtures/test_config.yaml config/processing.yaml
    canvodpy config validate
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

if [ -f config/processing.yaml ]; then
    echo "Validating configuration..."
    if ! canvodpy config validate; then
        echo "❌ Configuration validation failed"
        exit 1
    fi
    echo "✓ Configuration is valid"
fi
```

### Docker Entrypoint

```bash
#!/bin/bash
# docker-entrypoint.sh

echo "Validating configuration..."
if ! canvodpy config validate; then
    echo "❌ Invalid configuration"
    exit 1
fi

echo "Starting processing..."
exec python -m canvodpy.main "$@"
```
