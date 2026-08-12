# ⚡ ptop

**ptop** is a next-generation terminal system monitor built with **Python**, **Textual**, and **uv**. Inspired by `btop`, `ptop` brings high-density Unicode Braille sparklines, a rich async architecture, modular layout presets, interactive process management, and live health alerting into an extensible Python tool.

---

## ✨ Key Features (Better than btop)

- **⚡ Modern Async Architecture**: Powered by `Textual` and `asyncio` with non-blocking background thread pool metrics sampling. Zero UI stuttering even under heavy system load.
- **📈 High-Resolution Unicode Braille Sparklines**: Multi-level Braille sub-pixel chart rendering for CPU, RAM, Disk I/O, Network RX/TX, and GPU graphs.
- **🎨 Built-in Theme Suite**: Instantly cycle between 5 themes on the fly (`B` key):
  - **Catppuccin Mocha** (Default)
  - **Tokyo Night**
  - **Nord**
  - **Dracula**
  - **Cyberpunk**
- **📐 Layout Presets**: Switch between dashboard views (`L` key):
  - **Full**: Complete multi-column panel view (CPU, Memory, Disk, Network, GPU, Processes).
  - **Compact**: Single-column compact monitoring layout.
  - **GPU Focus**: Dedicated view emphasizing GPU hardware, VRAM, and temperatures.
  - **Process Focus**: Maximum screen space dedicated to interactive process management.
- **🌳 Interactive Process Manager**:
  - **Process Tree View** (`T` key) with parent-child process hierarchy.
  - **Fuzzy Search & Filtering** (`/` key) by PID, name, user, or command line.
  - **Process Inspector** (`I` / `Enter` key) displaying open files, network connections, memory info, threads.
  - **Signal Sender** (`K` key) to send `SIGKILL (9)`, `SIGTERM (15)`, `SIGSTOP (19)`, `SIGCONT (18)`.
  - **Multi-column Sorting** (`S` key) by CPU%, MEM%, PID, Name, Disk I/O, or User.
  - **Container Detection**: Automatic detection of Docker/Podman containerized processes.
- **⚠️ Smart Health & Alerts**: Live system health evaluation drawer (`A` key) alerting on thermal throttling, high memory pressure, runaway CPU processes, and low disk space.

---

## 🚀 Quick Start with `uv`

### Running directly with `uv`
```bash
uv run ptop
```

### Command Line Options
```bash
# Start with Tokyo Night theme and Compact layout
uv run ptop --theme tokyonight --layout compact

# Set custom refresh rate (500ms)
uv run ptop --refresh 500
```

### Installation as a tool
```bash
uv tool install .
ptop
```

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
| --- | --- |
| `B` | Cycle Color Themes (Catppuccin, TokyoNight, Nord, Dracula, Cyberpunk) |
| `L` | Cycle Layout Presets (Full, Compact, GPU Focus, Process Focus) |
| `S` | Cycle Process Sort Column (CPU%, MEM%, PID, Name, Disk I/O, User) |
| `R` | Reverse Sort Direction |
| `T` | Toggle Process Tree View |
| `/` | Search / Filter Processes |
| `Esc` | Clear Active Filter |
| `I` / `Enter` | Inspect Process Details (Open Files, Net Connections) |
| `K` | Send Signal to Process (SIGKILL 9, SIGTERM 15, etc.) |
| `A` | Toggle System Health Alerts Drawer |
| `?` | Open Help Modal |
| `Q` | Quit `ptop` |

---

## 🛠️ Development & Testing

Run unit tests using `pytest` via `uv`:

```bash
uv run pytest
```

---

## 📄 License

MIT License
