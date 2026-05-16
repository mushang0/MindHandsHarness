<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/83dac4d5-d891-4bd4-b02f-93b3cbe64dbc" />

# MindHandsHarness

**A specification-driven multi-agent software engineering workflow.**

MindHandsHarness is not just a tool—it's an engineering governance protocol. It transforms AI from a "chat-based guesser" into a "disciplined software engineer" by separating strategic planning from mechanical execution.

[中文说明](README.zh-CN.md)

---

# 🛑 Why? The "Drunken Walk" Problem

Most AI coding sessions start strong but inevitably fail as they grow. You've likely experienced these **Core Pain Points**:
- **Context Pollution**: Your AI gets lost in its own chat history and execution logs, leading to hallucinations and "forgetting" requirements.
- **Silent Architecture Creep**: A coder agent starts a small refactor and ends up silently redesigning your entire database because it "thought it was better."
- **Spec Drift**: The implementation slowly drifts away from your original intent because there is no "source of truth" outside the chat window.
- **Token Explosion**: You're paying for 32k tokens of garbage context in every single turn.

---

# 💡 The Solution: Protocol over Prompting

MindHandsHarness treats AI coordination as an **engineering governance problem**. It enforces three unbreakable walls:

### 1. Specification-Gated Execution
**No Spec, No Code.** The "Brain" must freeze a versioned Implementation Spec before any code is changed. The Coder is physically unable to "invent" requirements—it only executes the spec.

### ### 2. Context Isolation
**Context is a Liability.** Every sub-task (Reading, Coding, Testing) runs in an isolated, one-shot session. Workers only see what they *must* see. This preserves reasoning quality and slashes token costs.

### 3. Persistent Engineering Memory
**Intent vs. History.** Strategic decisions are externalized into `.harness/` artifacts. Future tasks inherit stable "Engineering Intent" instead of fragile "Chat History."

---

# 🚀 Quick Start (30 Seconds)

To use MindHandsHarness in your existing project:

### 1. Clone & Integrate
```bash
# Clone the repository
git clone https://github.com/mushang0/MindHandsHarness.git

# Move core protocol files to your project root
cp -r MindHandsHarness/.harness /path/to/your/project/
cp MindHandsHarness/AGENTS.md /path/to/your/project/
```

### 2. Activate & Chat
Open your AI editor (Cursor, Claude Code, etc.) in your project and say:
> "Follow the `AGENTS.md` protocol to [Your Goal]."

---

# 🛠 Interaction Example: JWT Auth

**User**: *"Use the harness to add JWT authentication."*

**AI (Brain)**: *"Mission M-001 started. I'm dispatching a **Reader** to find the auth insertion points. Please run the worker instruction below."*

**User**: (Runs worker) *"Reader done."*

**AI (Brain)**: *"Evidence collected. I've written the **Implementation Spec** (v1). It enforces `jsonwebtoken` and a 7-day expiry. **Approve?**"*

**User**: *"Approve."*

**AI (Brain)**: *"Spec frozen. Dispatching **Coder** to execute. Run the Coder instruction."*

**User**: (Runs worker) *"Coder done."*

**AI (Brain)**: *"Mission complete. Intent preserved. Spec satisfied."*

---

# 📂 Repository Structure

- `.harness/`: The Protocol Engine. Contains role prompts, task logic, and state management.
- `AGENTS.md`: The "AI Constitution." **You should customize this file** to add your project-specific coding standards and rules.
- `bin/harness.py`: The State Manager. Automates agent coordination and artifact tracking.
