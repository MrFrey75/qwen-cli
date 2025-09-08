# 🗺️ Qwen CLI Roadmap (AI-Readable)

This document defines the **phased evolution** of Qwen CLI.  
Each phase is **atomic**, **opt-in**, **local-first**, **testable**, and **extensible**.

---

## 🧭 Phases

### 🟢 Phase 0: CLI Foundation
- [x] `qwen --help` shows help
- [x] `qwen --version` shows version
- [x] Installable via `pip install -e .`
- [x] Runs without external dependencies
- ✅ Success: CLI works locally and prints usage

---

### 🔜 Phase 1: Local LLM Integration
**Goal**: Connect to Ollama and query Qwen model.

#### Features
- Detect if `http://localhost:11434` (Ollama) is running
- Pull `qwen:latest` with user confirmation
- `qwen ask "What is Python?"` → returns AI response

#### Success Criteria
- Response generated locally
- Error if Ollama not running
- No auto-download without consent

#### Status
- Complete
- Tested with Ollama and Qwen
- Works offline once model is local

---

### 🔜 Phase 2: Session Context
**Goal**: Maintain short-term memory in one session.

#### Features
- `qwen chat` starts interactive mode
- Remembers prior messages in session
- In-memory only (no disk)

#### Success Criteria
- 5+ turn conversation works
- Context resets on exit

#### Status
- In progress

---

### 🔜 Phase 3: Persistent History (Opt-in)
**Goal**: Save/load chat history from disk.

#### Features
- Save to `~/.qwen/history/YYYY-MM-DD-HH-MM-SS.json`
- Load with `qwen chat --session <id>`
- Disabled by default

#### Privacy
- All files local
- Clear data policy
- User can delete anytime
- 
#### Status
- Planned

---

### 🔜 Phase 4: Command Suggestions
**Goal**: Turn natural language into shell commands.

#### Features
- `qwen suggest "find all .py files > 1MB"`
  → Suggests: `find . -name "*.py" -size +1M`
- Optional `--execute` with confirmation

#### Safety
- Never auto-execute
- Always show command first
- 
#### Status
- Planned

---

### 🔜 Phase 5: Plugin System
**Goal**: Support AI-generated plugins.

#### Features
- Plugins in `~/.qwen/plugins/`
- Manifest: `plugin.yaml` + Python module
- Example: `todo`, `git-helper`, `weather`
- AI can generate & install with approval
- 
#### Status
- Planned

---

### 🔜 Phase 6: Multimodal Input
**Goal**: Accept images via local multimodal models (e.g., Qwen-VL via Ollama).

#### Features
- `qwen describe image.png`
- Works offline
- Fallback if model not available
- 
#### Status
- Planned

---

### 🔜 Phase 7: Voice Interface (Experimental)
**Goal**: Voice-to-text and text-to-speech using local tools.

#### Features
- `qwen listen` – start voice input
- Optional speech output
- Full offline support
- 
#### Status
- Planned

---

## 🔄 Development Principles
- **Atomic**: One thing per phase
- **Opt-in**: Nothing activates silently
- **Local-first**: Data never leaves device
- **Testable**: Clear success criteria
- **Extensible**: Built for AI-assisted growth
