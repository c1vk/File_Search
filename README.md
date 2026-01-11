# File Search Engine (Desktop)

A fast, minimal desktop file search engine focused on **user productivity**, inspired by tools like *Everything*, *Alfred*, and *Raycast* — but built from scratch for learning systems, UI, and indexing.

This project provides **instant filename-based search**, a clean UI, and a scalable architecture that avoids full rescans by using indexing and filesystem watchers.

---

##  Features

*  **Fast filename search** using a local SQLite index
*  **Indexed search** (no repeated full scans)
* ️ **Minimal, distraction-free UI** (PySide6 / Qt)
*  **Debounced queries** for smooth typing
*  **Smart path display** (home directory compacted)
*  **Background indexing & search threads**
*  **Incremental updates via file watchers** (no re-indexing entire directories)
*  Designed to scale to **10k+ results** (Model/View architecture planned)

---

##  UI Design Principles

* Frameless, always-on-top window
* Keyboard-first interaction (ESC to close)
* Minimal visual noise
* Designed for macOS, Linux, and Windows compatibility
* Avoids heavy widgets for scalability

---

##  Tech Stack

* **Language:** Python 3.10+
* **UI:** PySide6 (Qt)
* **Database:** SQLite
* **Filesystem Monitoring:** watchdog (planned)
* **Threading:** QThread (Qt-native)

---

##  Design Decisions

* System directories are intentionally skipped for safety & performance
* Reparse points (symlinks / junctions) are ignored to avoid loops
* UI result count is capped to maintain responsiveness
* Indexing and UI rendering are strictly separated

---

##  Development Notes

* This project prioritizes **learning system-level concepts** over shortcuts
* Architecture is intentionally modular for team collaboration
* Many decisions mirror real-world desktop tools

---

##  Team & Contribution

This project is built by a small team:

* UI & architecture
* Indexing & filesystem logic
* Search ranking & filtering

Contributions, suggestions, and architectural discussions are welcome.

---

## Learning Goals

* Desktop UI engineering with Qt
* Filesystem internals (Windows / Linux / macOS)
* Indexing & search systems
* Performance-aware UI design
* Cross-platform constraints