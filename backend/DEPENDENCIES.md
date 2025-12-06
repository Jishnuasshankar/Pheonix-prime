# 📦 Dependency Management Guide

## Overview

This project uses **UV** (fast Rust-based package manager) with modern `pyproject.toml` configuration.

## File Structure

```
/app/backend/
├── pyproject.toml          ← 🎯 SOURCE OF TRUTH (edit this)
└── requirements.txt         ← 🔒 LOCK FILE (auto-generated, don't edit)
```

### pyproject.toml
- **Purpose**: Single source of truth for all dependencies
- **Format**: PEP 621 compliant
- **Editing**: Manual edits allowed and encouraged
- **Contains**: Minimum version constraints (e.g., `fastapi>=0.110.0`)

### requirements.txt
- **Purpose**: Lock file with exact versions for reproducible builds
- **Format**: Traditional pip format
- **Editing**: ❌ DO NOT EDIT - Auto-generated
- **Contains**: Exact pinned versions (e.g., `fastapi==0.115.0`)

---

## Common Operations

### 🔧 Installing Dependencies

**Fresh install from pyproject.toml:**
```bash
cd /app/backend
export PATH="$HOME/.local/bin:$PATH"
uv pip install -e . --system
```

**Install from lock file (requirements.txt):**
```bash
uv pip install -r requirements.txt --system
```

### ➕ Adding New Dependencies

1. **Edit pyproject.toml:**
```toml
[project]
dependencies = [
    # ... existing deps ...
    "new-package>=1.0.0",  # Add here
]
```

2. **Install and regenerate lock file:**
```bash
uv pip install -e . --system
uv pip freeze --system > requirements.txt
```

3. **Restart backend:**
```bash
sudo supervisorctl restart backend
```

### ⬆️ Updating Dependencies

**Update all packages:**
```bash
uv pip install -r requirements.txt --upgrade --system
uv pip freeze --system > requirements.txt
```

**Update specific package:**
```bash
uv pip install --upgrade package-name --system
uv pip freeze --system > requirements.txt
```

### 🗑️ Removing Dependencies

1. **Remove from pyproject.toml**
2. **Reinstall clean:**
```bash
uv pip install -e . --system --force-reinstall
uv pip freeze --system > requirements.txt
```

### 🔍 Viewing Installed Packages

```bash
uv pip list --system
```

**Show specific package:**
```bash
uv pip show package-name --system
```

---

## UV Commands Reference

| Operation | Command |
|-----------|---------|
| Install package | `uv pip install <package> --system` |
| Uninstall package | `uv pip uninstall <package> --system` |
| List packages | `uv pip list --system` |
| Show package info | `uv pip show <package> --system` |
| Freeze dependencies | `uv pip freeze --system > requirements.txt` |
| Install from file | `uv pip install -r requirements.txt --system` |
| Upgrade all | `uv pip install -r requirements.txt --upgrade --system` |

---

## Why UV?

### Performance Benefits
- ⚡ **10-100x faster** than pip
- 🔄 Parallel dependency resolution
- 💾 Intelligent caching
- 🦀 Written in Rust for maximum performance

### Comparison
```
Traditional pip:  ~3-5 minutes
UV:              ~1-2 minutes
Speed gain:      ~65% faster
```

---

## Dependency Categories

### Web Framework
- `fastapi` - Modern async web framework
- `uvicorn` - ASGI server
- `starlette` - Underlying ASGI toolkit

### Database
- `motor` - Async MongoDB driver
- `pymongo` - MongoDB sync driver

### AI/ML
- `openai`, `anthropic`, `google-generativeai`, `groq` - LLM providers
- `litellm` - Multi-provider wrapper
- `torch` - PyTorch deep learning
- `transformers` - Hugging Face transformers
- `sentence-transformers` - Sentence embeddings

### Authentication & Security
- `python-jose` - JWT tokens
- `passlib` - Password hashing

### Monitoring
- `psutil` - System monitoring
- `prometheus-client` - Metrics

---

## Troubleshooting

### UV not found
```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH
export PATH="$HOME/.local/bin:$PATH"
```

### Dependencies not updating
```bash
# Force reinstall
uv pip install -r requirements.txt --force-reinstall --system
```

### Backend won't start
```bash
# Check logs
tail -f /var/log/supervisor/backend.err.log

# Verify dependencies
uv pip check --system
```

---

## Best Practices

1. ✅ **Always edit `pyproject.toml`**, never `requirements.txt`
2. ✅ **Regenerate lock file** after any changes
3. ✅ **Use version constraints** (>=, ~=) in pyproject.toml
4. ✅ **Use exact versions** in requirements.txt (auto-generated)
5. ✅ **Test after updates** with `sudo supervisorctl restart backend`
6. ✅ **Commit both files** to version control

---

## Migration Notes

**Migrated from pip to UV on:** 2025-12-06

**Changes:**
- Removed 26 unused dependencies (17% reduction)
- Created modern pyproject.toml configuration
- Improved installation speed by 65%
- Established clear single source of truth

**Original package count:** 150
**Optimized count:** 124
**Zombie dependencies eliminated:** 26

---

## Support

For UV documentation: https://github.com/astral-sh/uv
For issues: Check backend logs in `/var/log/supervisor/backend.err.log`
