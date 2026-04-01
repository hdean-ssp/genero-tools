# genero-tools Documentation

Welcome to genero-tools! This is your complete guide to extracting and analyzing Genero/4GL codebases.

---

## 🚀 Quick Start (5 minutes)

### 1. Generate Metadata
```bash
bash generate_all.sh /path/to/genero/code
bash query.sh create-dbs
```

### 2. Run Your First Query
```bash
bash query.sh find-function "my_function"
bash query.sh search-functions "get_*"
bash query.sh find-function-dependencies "my_function"
```

### 3. Verify Everything Works
Follow [COMMAND_LINE_TESTING_CHECKLIST.md](COMMAND_LINE_TESTING_CHECKLIST.md) (30 tests, 15 minutes)

---

## 📚 Documentation by Role

### I'm New to genero-tools
1. Read this README (you're here!)
2. Follow [COMMAND_LINE_TESTING_CHECKLIST.md](COMMAND_LINE_TESTING_CHECKLIST.md) - Verify all features work
3. Reference [QUERYING.md](QUERYING.md) - Find any command

**Time:** 30 minutes → Ready to use

### I Need a Specific Command
- **Quick lookup:** See "Common Commands" section below
- **Complete reference:** [QUERYING.md](QUERYING.md)
- **With examples:** [COMMAND_LINE_TESTING_GUIDE.md](COMMAND_LINE_TESTING_GUIDE.md)

### I'm Setting Up Vim Integration
- [VIM_PLUGIN_INTEGRATION_GUIDE.md](VIM_PLUGIN_INTEGRATION_GUIDE.md) - Setup instructions
- [VIM_OUTPUT_FORMATS.md](VIM_OUTPUT_FORMATS.md) - Output format specifications

### I'm Developing genero-tools
- [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) - Development workflow
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Recent improvements

### I Need to Understand the System
- [FEATURES.md](FEATURES.md) - What genero-tools can do
- [ARCHITECTURE.md](ARCHITECTURE.md) - How it works
- [TYPE_RESOLUTION_GUIDE.md](TYPE_RESOLUTION_GUIDE.md) - Type resolution details

---

## 🔍 Common Commands

### Finding Functions
```bash
bash query.sh find-function "my_function"           # Find specific function
bash query.sh search-functions "get_*"              # Search by pattern
bash query.sh list-file-functions "path/to/file"   # List functions in file
```

### Understanding Dependencies
```bash
bash query.sh find-function-dependencies "func"    # What does it call?
bash query.sh find-function-dependents "func"      # What calls it?
bash query.sh find-dead-code                       # Find unused functions
```

### Working with Modules
```bash
bash query.sh find-module "core"                   # Find module
bash query.sh search-modules "*"                   # Search modules
bash query.sh find-functions-in-module "core"      # Functions in module
```

### Finding References & Authors
```bash
bash query.sh find-reference "PRB-299"             # Find code reference
bash query.sh find-author "John"                   # Find author
bash query.sh author-expertise "John"              # Author expertise
```

### Type Resolution
```bash
bash query.sh find-function-resolved "func"        # Resolved types
bash query.sh unresolved-types                     # Find unresolved types
bash query.sh validate-types                       # Validate consistency
```

### Output Formats (Vim Integration)
```bash
bash query.sh find-function "func" --format=vim           # Single-line
bash query.sh find-function "func" --format=vim-hover     # Hover tooltip
bash query.sh search-functions "*" --format=vim-completion # Completion
```

---

## 📖 Complete Documentation

| Document | Purpose | Time |
|----------|---------|------|
| **[COMMAND_LINE_TESTING_CHECKLIST.md](COMMAND_LINE_TESTING_CHECKLIST.md)** | 30 tests to verify all features | 15 min |
| **[QUERYING.md](QUERYING.md)** | Complete query reference | 20 min |
| **[COMMAND_LINE_TESTING_GUIDE.md](COMMAND_LINE_TESTING_GUIDE.md)** | Comprehensive guide with all options | 30 min |
| **[FEATURES.md](FEATURES.md)** | Feature overview | 10 min |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | System design | 20 min |
| **[DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)** | Development workflow | 15 min |
| **[TYPE_RESOLUTION_GUIDE.md](TYPE_RESOLUTION_GUIDE.md)** | Type resolution system | 15 min |
| **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** | Recent improvements | 10 min |
| **[VIM_PLUGIN_INTEGRATION_GUIDE.md](VIM_PLUGIN_INTEGRATION_GUIDE.md)** | Vim setup | 15 min |
| **[VIM_OUTPUT_FORMATS.md](VIM_OUTPUT_FORMATS.md)** | Output format specs | 10 min |
| **[SECURITY.md](SECURITY.md)** | Security practices | 10 min |

---

## 🎯 Learning Paths

### Path 1: Quick Start (30 minutes)
1. This README (5 min)
2. [COMMAND_LINE_TESTING_CHECKLIST.md](COMMAND_LINE_TESTING_CHECKLIST.md) (15 min)
3. [QUERYING.md](QUERYING.md) (10 min)

**Result:** Ready to use genero-tools

### Path 2: Complete Learning (2 hours)
1. This README (5 min)
2. [FEATURES.md](FEATURES.md) (10 min)
3. [COMMAND_LINE_TESTING_CHECKLIST.md](COMMAND_LINE_TESTING_CHECKLIST.md) (15 min)
4. [COMMAND_LINE_TESTING_GUIDE.md](COMMAND_LINE_TESTING_GUIDE.md) (30 min)
5. [QUERYING.md](QUERYING.md) (15 min)
6. [TYPE_RESOLUTION_GUIDE.md](TYPE_RESOLUTION_GUIDE.md) (15 min)
7. [VIM_PLUGIN_INTEGRATION_GUIDE.md](VIM_PLUGIN_INTEGRATION_GUIDE.md) (15 min)
8. [ARCHITECTURE.md](ARCHITECTURE.md) (15 min)

**Result:** Expert user

### Path 3: Developer Setup (3 hours)
1. [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) (30 min)
2. [ARCHITECTURE.md](ARCHITECTURE.md) (30 min)
3. [COMMAND_LINE_TESTING_GUIDE.md](COMMAND_LINE_TESTING_GUIDE.md) (30 min)
4. [TYPE_RESOLUTION_GUIDE.md](TYPE_RESOLUTION_GUIDE.md) (20 min)
5. [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) (20 min)

**Result:** Ready to develop genero-tools

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| Database not found | `bash query.sh create-dbs` |
| No results | `sqlite3 workspace.db "SELECT COUNT(*) FROM functions;"` |
| Permission denied | `chmod +x *.sh src/*.sh` |
| Python error | `python3 --version` (need 3.6+) |
| Slow queries | `bash query.sh create-dbs` |

See [COMMAND_LINE_TESTING_GUIDE.md](COMMAND_LINE_TESTING_GUIDE.md) for detailed troubleshooting.

---

## 📊 What's New

**April 1, 2026:**
- ✅ Fixed type resolution for LIKE references (96% success rate)
- ✅ Added variables per function storage
- ✅ Added modulars (GLOBALS/IMPORT) per file storage
- ✅ Consolidated documentation for clarity

See [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for details.

---

## 🔗 API Documentation

Complete API reference available in `docs/api/`:
- [api/00-START-HERE.md](api/00-START-HERE.md) - API quick start
- [api/QUICK_REFERENCE.md](api/QUICK_REFERENCE.md) - API reference
- [api/MANIFEST.md](api/MANIFEST.md) - API manifest

---

## 📝 File Organization

```
docs/
├── README.md                           ← You are here
├── COMMAND_LINE_TESTING_CHECKLIST.md   ← Verify everything works
├── QUERYING.md                         ← Query reference
├── COMMAND_LINE_TESTING_GUIDE.md       ← Complete guide
├── FEATURES.md                         ← Feature overview
├── ARCHITECTURE.md                     ← System design
├── DEVELOPER_GUIDE.md                  ← Development guide
├── TYPE_RESOLUTION_GUIDE.md            ← Type resolution
├── IMPLEMENTATION_SUMMARY.md           ← Recent improvements
├── VIM_PLUGIN_INTEGRATION_GUIDE.md     ← Vim setup
├── VIM_OUTPUT_FORMATS.md               ← Output formats
├── SECURITY.md                         ← Security practices
├── api/                                ← API documentation
└── .archive/                           ← Archived docs
```

---

## ✨ Key Features

- **Function Analysis** - Find, search, and understand functions
- **Dependency Analysis** - See what calls what
- **Module Management** - Organize and query modules
- **Code Quality** - Analyze complexity and metrics
- **Type Resolution** - Resolve LIKE references to schema types
- **IDE Integration** - Use with Vim and other editors
- **Batch Queries** - Process multiple queries at once
- **Performance** - <1ms for exact lookups

---

## 🚀 Next Steps

1. **Get Started:** Follow the Quick Start section above
2. **Verify:** Run [COMMAND_LINE_TESTING_CHECKLIST.md](COMMAND_LINE_TESTING_CHECKLIST.md)
3. **Learn:** Choose a learning path above
4. **Reference:** Use [QUERYING.md](QUERYING.md) for commands
5. **Integrate:** Set up Vim with [VIM_PLUGIN_INTEGRATION_GUIDE.md](VIM_PLUGIN_INTEGRATION_GUIDE.md)

---

**Last Updated:** April 1, 2026  
**Version:** 1.0.0

