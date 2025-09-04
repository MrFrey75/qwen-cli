# 📄 **Qwen CLI – AI-Readable Requirements Specification**

## 🎯 Vision
A secure, extensible, personal AI assistant that evolves from a simple CLI into a multimodal, context-aware companion — built one safe, verifiable step at a time.

---

## 🔁 Development Principles
- **Atomic**: Each phase does one thing well.
- **Opt-in**: Nothing activates without consent.
- **Local-first**: All sensitive data stays on-device.
- **Testable**: Every phase has clear success criteria.
- **Extensible**: Designed for AI-assisted evolution.

---

## Source

- **Repo**: [https://github.com/MrFrey75/Gwen-CLI.git](https://github.com/MrFrey75/Gwen-CLI.git)

# 🔢 Phase Breakdown

---

### 🔹 Phase 0: Project & Workspace Initialization  
**Goal**: Create the foundation: workspace, config, and string system.

#### ✅ Features
- Define workspace: default `~/.qwen-cli` or via `--dir`
- Create directory if missing
- Generate `config.json` with:
  ```json
  { "model": "qwen-max", "temperature": 0.7, "top_p": 0.8, "max_tokens": 2048, "stream": true }
  ```
- Create `strings.json` with all UI messages (externalized)
- Create `.setup_complete` flag file
- Add `--init` to run this setup

#### 📁 Files Created
```
config.json
strings.json
.setup_complete
```

#### 🧪 Success Criteria
- Running `qwen-cli --init` creates the workspace
- Files are readable and valid JSON
- No sensitive data stored

---

### 🔹 Phase 1: CLI Argument Parsing  
**Goal**: Parse user input and distinguish modes.

#### ✅ Features
- Support:
  - `qwen-cli "Hello"` → one-shot mode
  - `qwen-cli` → interactive mode
  - `--init` → setup
  - `--dir <path>` → custom workspace
- Validate `DASHSCOPE_API_KEY` exists in environment
- Show help with `--help`

#### 🧪 Success Criteria
- Args parsed correctly
- One-shot and interactive modes detected
- Missing API key shows clear error

---

### 🔹 Phase 2: Basic API Interaction  
**Goal**: Send a message to Qwen and receive a response.

#### ✅ Features
- Use `dashscope.Generation.call()`
- Pass prompt from CLI
- Print response
- Handle errors gracefully
- No streaming yet

#### 🔗 Dependencies
- `dashscope>=1.14.0`

#### 🧪 Success Criteria
- `qwen-cli "Say hello"` returns a real Qwen response
- Errors show clear message
- Uses model from `config.json`

---

### 🔹 Phase 3: Streaming Output  
**Goal**: Enable real-time token streaming.

#### ✅ Features
- Add `stream=True` to API call
- Print tokens as they arrive
- No buffering
- Maintain `--no-stream` option (future)

#### 🧪 Success Criteria
- Response appears character-by-character
- No delay until full response

---

### 🔹 Phase 4: Interactive Chat Mode  
**Goal**: Support multi-turn conversation in terminal.

#### ✅ Features
- Loop: `input() → send → print → repeat`
- Exit on `exit`, `quit`, `bye`
- Maintain in-memory message list
- Show user and AI labels

#### 🧪 Success Criteria
- User can have a back-and-forth chat
- Responses are context-free (no memory yet)

---

### 🔹 Phase 5: Message History Logging  
**Goal**: Log all interactions to disk.

#### ✅ Features
- Append each message to `history.jsonl`
- Format: `{"timestamp": "...", "role": "user|assistant", "content": "..."}`
- One JSON object per line

#### 📁 Files
```
history.jsonl
```

#### 🧪 Success Criteria
- File grows with each message
- Valid JSONL
- Can be read later

---

### 🔹 Phase 6: Configuration Loading  
**Goal**: Load settings from `config.json`.

#### ✅ Features
- Read `config.json` at startup
- Use values for API call
- Fallback to defaults if missing

#### 🧪 Success Criteria
- Changing `temperature` in config affects output
- Invalid JSON shows error

---

### 🔹 Phase 7: Save Configuration  
**Goal**: Allow user to persist CLI overrides.

#### ✅ Features
- Add `--save-config`
- Save current model, temp, etc. to `config.json`
- Only save user-changed fields

#### 🧪 Success Criteria
- `gwen-cli --model qwen-turbo --save-config` updates `config.json`

---

### 🔹 Phase 8: User Profile Creation  
**Goal**: Create `user.json` to store preferences.

#### ✅ Features
- On first run, create `user.json`:
  ```json
  {
    "created_at": "ISO",
    "last_used": "ISO",
    "preferences": {},
    "consent": {}
  }
  ```

#### 📁 Files
```
user.json
```

#### 🧪 Success Criteria
- File created during `--init`
- Valid JSON

---

### 🔹 Phase 9: First-Time Setup Wizard  
**Goal**: Guide user through initial configuration.

#### ✅ Features
- Run if `.setup_complete` missing
- Prompt for:
  - API key (not saved)
  - Model choice
  - Tone (neutral, friendly, etc.)
  - Response length
- Save to `config.json` and `user.json`
- Create `.setup_complete`

#### 🧪 Success Criteria
- Wizard runs only once
- Config and user files updated

---

### 🔹 Phase 10: Privacy Consent Collection  
**Goal**: Ask for permission to store personal data.

#### ✅ Features
- In setup, ask:
  - “Allow storing personal data locally? (yes/no)”
- If yes:
  - Set `user.json` → `"consent": { "privacy_consent_given": true }`
- If no:
  - Disable sensitive storage

#### 🧪 Success Criteria
- Consent recorded in `user.json`
- No secrets allowed if denied

---

### 🔹 Phase 11: Encrypted Secret Storage (Setup)  
**Goal**: Prepare secure storage system.

#### ✅ Features
- On consent, generate `.key.enc` using `Fernet.generate_key()`
- Set file permissions to `0o600`
- Never expose key

#### 📁 Files
```
.key.enc
```

#### 🧪 Success Criteria
- Key file created
- Not readable by other users

---

### 🔹 Phase 12: Store & Retrieve Secrets  
**Goal**: Save and read encrypted data.

#### ✅ Features
- Add `--secret key value` → encrypt and save to `secrets.json`
- Add `--list-secrets` → show keys only
- Add `--forget key` → delete
- Use `cryptography.fernet.Fernet`

#### 📁 Files
```
secrets.json
```

#### 🧪 Success Criteria
- Secret stored encrypted
- `--list-secrets` hides values
- Can retrieve with `get_secret("key")`

---

### 🔹 Phase 13: Audit-Ready Consent Record  
**Goal**: Create a signed, tamper-evident consent log.

#### ✅ Features
- Generate `consent-<date>.json` on consent
- Include:
  - Timestamp
  - Purpose
  - Storage path
  - User agent (username, hostname)
  - Applied settings
- Compute SHA-256 → save to `consent.latest.sha256`

#### 📁 Files
```
consent-2025-04-05.json
consent.latest.sha256
```

#### 🧪 Success Criteria
- File created with full context
- Checksum matches content

---

### 🔹 Phase 14: Fact Detection (Name)  
**Goal**: Detect and optionally save user’s name.

#### ✅ Features
- Use `spacy.load("en_core_web_sm")`
- Detect `PERSON` entity in input
- If not already saved, ask: “Save your name?”
- Store in `facts.json`

#### 📁 Files
```
facts.json
```

#### 🔗 Dependencies
- `spacy`, `python-dateutil`

#### 🧪 Success Criteria
- “My name is Alice” → detects “Alice”
- Asks to save
- Stores in `facts.json`

---

### 🔹 Phase 15: Fact Detection (Birthday)  
**Goal**: Detect and offer to save birthday.

#### ✅ Features
- Use spaCy + regex to find `DATE` with “born”, “birthday”
- Parse with `dateutil.parse`
- Ask: “Save securely?”
- Save to `secrets.json` (if consented) or `facts.json`

#### 🧪 Success Criteria
- “I was born on June 5” → detects date
- Offers secure storage
- Respects consent

---

### 🔹 Phase 16: Context Injection  
**Goal**: Enrich prompts with user facts.

#### ✅ Features
- Before API call, build context:
  - `[Context: User name: Alice; User birthday: 0000-06-05]`
- Inject into prompt
- Do not expose raw secrets if not consented

#### 🧪 Success Criteria
- AI uses name in response
- No leakage of unconsented data

---

### 🔹 Phase 17: Personality Detection  
**Goal**: Detect natural-language tone requests.

#### ✅ Features
- Detect: “Be more enthusiastic”, “Talk like a scientist”
- Map to profile: temperature, tone, directive
- Update `user.json` and `facts.json`

#### 🧪 Success Criteria
- “Be funnier” → sets personality to “funny”
- AI responds with humor

---

### 🔹 Phase 18: Personality Injection  
**Goal**: Apply personality to responses.

#### ✅ Features
- Add `[Directive: Respond in a witty style]` to prompt
- Adjust `temperature` dynamically
- Confirm change: “Got it! I’ll be more enthusiastic.”

#### 🧪 Success Criteria
- AI changes tone
- Settings persist

---

### 🔹 Phase 19: Self-Analysis (Read-Only)  
**Goal**: Allow app to read its own code and logs.

#### ✅ Features
- Add `--analyze-self` (opt-in)
- Read:
  - Python files
  - `history.jsonl`
  - `config.json`
- Generate summary: “You use birthday tracking often.”

#### 🧪 Success Criteria
- Report generated
- No code changes made

---

### 🔹 Phase 20: Voice Input (Local ASR)  
**Goal**: Add speech-to-text using local model.

#### ✅ Features
- Add `--voice` mode
- Use `vosk` or `whisper.cpp` for offline transcription
- Record from mic
- Convert to text → send to Qwen

#### 🧪 Success Criteria
- “Hello” spoken → sent to API
- Works without internet

---

### 🔹 Phase 21: Text-to-Speech  
**Goal**: Speak responses aloud.

#### ✅ Features
- Use `silero` or `pyttsx3` for TTS
- Play response after receiving
- Respect `voice_muted` flag

#### 🧪 Success Criteria
- AI speaks response
- No delay

---

### 🔹 Phase 22: Wake Word Detection  
**Goal**: Listen passively for activation phrase.

#### ✅ Features
- Run background listener
- Detect “hey qwen” using Vosk or Silero VAD
- Activate only after wake
- No cloud processing

#### 🧪 Success Criteria
- “hey qwen” → “I'm here!”
- Silent otherwise

---

### 🔹 Phase 23: Conversational Voice Mode  
**Goal**: Support multi-turn voice chat.

#### ✅ Features
- After wake, stay active for 30s
- Accept multiple inputs
- Respond via TTS
- Exit on silence or “stop”

#### 🧪 Success Criteria
- Multi-turn voice chat works
- No re-wake needed

---

### 🔹 Phase 24: Camera Access & Frame Capture  
**Goal**: Access camera safely.

#### ✅ Features
- Add `--vision` commands
- Open camera stream
- Capture single frame
- Respect privacy shutter

#### 🧪 Success Criteria
- Frame captured
- No background recording

---

### 🔹 Phase 25: Object Detection  
**Goal**: Recognize common items in view.

#### ✅ Features
- Use `YOLOv8` or `MobileViT`
- Detect: laptop, phone, cup
- Describe scene: “I see your water bottle.”

#### 🧪 Success Criteria
- Object detected
- Description accurate

---

### 🔹 Phase 26: Person Recognition (Opt-In)  
**Goal**: Learn and recognize known people.

#### ✅ Features
- `--learn-person "Alice"` → capture face embedding
- Store in `people/` (encrypted)
- Recognize on sight
- `--forget-person` to delete

#### 🧪 Success Criteria
- “Is Alice here?” → correct answer
- No raw images stored

---

### 🔹 Phase 27: Infrared & Low-Light Support  
**Goal**: Work in darkness.

#### ✅ Features
- Support IR cameras
- Use grayscale processing
- Detect motion and presence
- Work with NoIR or FLIR

#### 🧪 Success Criteria
- Detects person in dark
- No visible light needed

---

### 🔹 Phase 28: Visual Memory  
**Goal**: Remember object locations.

#### ✅ Features
- Track last seen location
- Answer: “Where’s my wallet?”
- Detect changes: “Your bag is missing”

#### 🧪 Success Criteria
- Accurate location memory
- Timely alerts

---

# ✅ Final Structure (Modular)

```
qwen_cli/
├── core/
│   ├── workspace.py
│   ├── config.py
│   ├── cli.py
│   └── chat.py
├── auth/
│   └── secrets.py
├── memory/
│   ├── facts.py
│   └── context.py
├── voice/
│   ├── asr.py
│   └── tts.py
└── vision/
    ├── camera.py
    └── detect.py

<workspace>/
├── config.json
├── user.json
├── secrets.json
├── facts.json
├── history.jsonl
├── strings.json
├── .key.enc
├── consent-*.json
├── voice.json
└── vision.json
```

---

# 🚫 Hard Constraints (All Phases)

- ❌ No feature activates without consent
- ❌ No data leaves device unless opted in
- ❌ No background recording
- ❌ No facial recognition without opt-in
- 🔐 All sensitive data encrypted
- 📝 All actions auditable

---

# 🧪 AI Code Generation Rules

When generating:
1. **Do one phase at a time**
2. **Only use dependencies declared**
3. **Never hardcode strings**
4. **Write tests for each phase**
5. **Preserve modularity**
6. **Validate inputs**

---

This document is now **ready for AI-driven implementation**.

Say:
> **"Generate Phase 0"**  
> or  
> **"Write tests for Phase 14"**

And I’ll deliver clean, secure, production-ready code — one atomic step at a time. 🚀