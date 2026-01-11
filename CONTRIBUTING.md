# Contributing Guide

Thanks for your interest in contributing to the **File Search Engine** project!
This document explains how to **set up the project locally**, understand the structure, and contribute safely.

---

## Local Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/c1vk/File_Search.git
cd File_Search
```

---

### 2. Install `uv`

You can install `uv` using **either** method below.

**Option 1: Using pip**

```bash
pip install uv
```

**Option 2: Using pipx (recommended)**

```bash
pipx install uv
```

> `pipx` keeps CLI tools isolated and avoids dependency conflicts.

---

### 3. Run the Application

```bash
uv run app/main.py
```

If the application window opens successfully, your setup is complete ✅

---

## Supported Platforms

* ✅ **Windows** (primary target)
* ⚠️ **Linux / macOS** (development only — behavior may differ)

> File indexing paths and filesystem behavior vary by OS.

---

## Contribution Workflow

1. Create a new branch:

   ```bash
   git checkout -b feature/<feature-name>
   ```
2. Make your changes
3. Test locally
4. Commit with a clear message
5. Open a pull request

---

## Notes for Contributors

* Keep UI changes platform-aware (Windows is the reference)
* Avoid blocking the UI thread with heavy filesystem operations
* Prefer incremental indexing over full re-indexing
* Follow existing project structure and naming conventions

Happy hacking 🚀
