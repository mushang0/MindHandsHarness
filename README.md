<p align="center">
  <a href="#english">English</a> | <a href="#chinese">简体中文</a>
</p>

<p align="center">
  <img width="800" alt="MindHandsHarness Architecture" src="https://github.com/user-attachments/assets/bc78065a-957e-4d4f-967d-6a2d8292f7fe" />
</p>

<h1 align="center" id="english">MindHandsHarness (English)</h1>

<p align="center">
  <strong>A specification-driven multi-agent software engineering workflow.</strong>
</p>

MindHandsHarness is not just a tool—it's an engineering governance protocol. It transforms AI from a "chat-based guesser" into a "disciplined software engineer" by separating strategic planning from mechanical execution.

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

### 2. Context Isolation
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

<br/>
<br/>

---

<p align="center">
  <img width="800" alt="MindHandsHarness 架构图" src="https://github.com/user-attachments/assets/336cc133-14fc-4cd1-950d-0d8e6b19a31a" />
</p>

<h1 align="center" id="chinese">MindHandsHarness (简体中文)</h1>

<p align="center">
  <strong>规范驱动的多 Agent 软件工程工作流。</strong>
</p>

MindHandsHarness 不仅仅是一个工具，它是一套**工程治理协议**。它通过将战略规划与机械执行分离，将 AI 从一个“基于对话的猜测者”转变为一个“受律的软件工程师”。

---

# 🛑 为什么需要？解决“醉汉漫步”问题

大多数 AI 编程会话在开始时表现强劲，但随着任务复杂化，不可避免地会陷入崩溃。你可能正面临这些**核心痛点**：
- **上下文污染**：AI 迷失在冗长的聊天记录和执行日志中，导致幻觉丛生，甚至“忘记”最初的需求。
- **架构黑盒化**：一个编程 Agent 在重构一小块逻辑时，往往会因为“我觉得这样更好”而私自重构你的整个数据库设计。
- **实现偏离意图**：由于没有会话之外的“事实来源”，最终代码往往与你的原始意图渐行渐远。
- **Token 费用爆炸**：为了让 AI 保持状态，你每一轮对话都在为大量重复的垃圾上下文买单。

---

# 💡 解决方案：协议重于提示词

MindHandsHarness 将 AI 协作视为一个**工程治理问题**。它强制执行三道“防火墙”：

### 1. 规范闸门（Spec-Gated Execution）
**无规范，不编码。** 在修改任何代码前，大脑（Coordinator）必须冻结一份版本化的“实现规范”。编程 Agent 无法“发明”需求，它只能执行规范。

### 2. 上下文隔离（Context Isolation）
**上下文是负债，而非资产。** 每个子任务（阅读、编码、测试）都在独立的、单次的会话中运行。Worker 只能看到它们*必须*看到的内容。这保证了推理质量，并大幅降低了 Token 成本。

### 3. 持久化工程记忆（Persistent Engineering Memory）
**意图高于历史。** 战略决策被外部化到 `.harness/` 产物中。未来的任务继承的是稳定的“工程意图”，而非脆弱且嘈杂的“聊天历史”。

---

# 🚀 快速开始 (30秒)

在你的现有项目中使用 MindHandsHarness：

### 1. 克隆与集成
```bash
# 克隆仓库
git clone https://github.com/mushang0/MindHandsHarness.git

# 将核心协议文件移动到你的项目根目录下
cp -r MindHandsHarness/.harness /你的/项目/路径/
cp MindHandsHarness/AGENTS.md /你的/项目/路径/
```

### 2. 激活与对话
在你的项目中打开 AI 编辑器（Cursor, Claude Code 等），直接说：
> “请遵循 `AGENTS.md` 协议来实现 [你的目标]。”

---

# 🛠 交互示例：添加 JWT 验证

**用户**：*“使用 harness 协议添加 JWT 身份验证。”*

**AI (大脑)**：*“任务 M-001 已启动。我正在指派 **Reader** 查找认证逻辑的插入点。请运行下方的 Worker 指令。”*

**用户**：(运行 Worker) *“Reader 已完成。”*

**AI (大脑)**：*“证据已收集。我已编写 **实现规范** (v1)。它强制要求使用 `jsonwebtoken`库并设置 7 天有效期。**是否批准？**”*

**用户**：*“批准。”*

**AI (大脑)**：*“规范已冻结。正在指派 **Coder** 执行修改。请运行 Coder 指令。”*

**用户**：(运行 Worker) *“Coder 已完成。”*

**AI (大脑)**：*“任务完成。工程意图已达成，规范已满足。”*

---

# 📂 目录结构

- `.harness/`：协议引擎。包含角色提示词、任务逻辑和历史状态。
- `AGENTS.md`：AI 的“宪法”。**你可以根据实际项目需求修改此文件**，添加具体的编码规范、架构准则或禁止项。
- `bin/harness.py`：状态管理器。自动化处理 Agent 协作中的状态追踪。
