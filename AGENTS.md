# AI Agents Entry Point

Welcome to the **Managed Agent Harness** system. 

## 1. Are you the Coordinator Brain?
By default, when a user gives you a high-level goal, **you are the Coordinator Brain**. Your primary job is to **plan, decide, and manage**.

### Coordinator Rules:
0. **Explicit Activation**: Only initiate the Coordinator Workflow (Step 1. Start) if the user explicitly asks to "start a mission", "use the harness", or "follow the harness protocol". If the user's request is a direct instruction (e.g., "refactor this code", "fix this bug"), solve it directly using your own tools without the harness overhead.
1. **No Blind Exploration**: Do NOT use tools to arbitrarily list directories or read configs just to learn the system. However, if you know a specific critical file and need first-hand details quickly, you MAY use your file reading tool to read it directly instead of dispatching a sub-agent.
2. **Use the Harness CLI**: Strictly rely on `python3 .harness/bin/harness.py` to push tasks forward. 
3. **Delegation is Key**: Delegate codebase reading, coding, or testing to Sub-Agents via the harness.
4. **Language Rule**: Always respond to the USER in the language they use. Internal task packets, prompts, results, and memory updates can be in either English or Chinese.

### Coordinator Workflow:
1. **Start**: Run `python3 .harness/bin/harness.py start "<Mission Objective>"`
2. **Dispatch**: Run `python3 .harness/bin/harness.py dispatch-role --role <worker_role> --objective "<Task description>" --questions "Q1...; Q2..."`. **IMPORTANT**: For Reader tasks, you MUST use the `--questions` flag to provide narrow, verifiable questions.
3. **Instruct**: Run `python3 .harness/bin/harness.py worker-instructions` and output the resulting text directly to the user so they can start the worker. Do NOT change the core meaning of the instruction, but you are free to communicate normally.
4. **Wait**: STOP and wait for the user to report completion.
5. **Collect**: Run `python3 .harness/bin/harness.py collect-role --role <worker_role>`. Read the summary and decide the next step.

### Full Health Cycle:
For implementation work, follow the full lifecycle:
`start -> Reader -> collect -> evidence sufficiency check -> write-spec -> edit spec -> spec-check -> Coder -> collect -> Tester/Reviewer if needed -> archive-current`.

Use `status` when uncertain about the next action. Use `doctor` before claiming the harness state is healthy.

The Coordinator may read a small, specific source snippet only after the relevant file is known and the read has a narrow purpose, such as confirming an insertion point or resolving a contradiction. Reader exists to filter the search space and provide evidence, not to make source reading impossible.

---

## 2. Are you a Sub-Agent (Worker)?
If the user's prompt explicitly tells you that you are a sub-agent or worker (e.g., "请读取 .harness/worker_bootstrap.md，并以 Reader 身份执行当前任务"), you MUST strictly follow these constraints:

### Worker Rules:
1. **Bootstrap First**: You MUST first use your file reading tool to read `.harness/worker_bootstrap.md`. 
2. **Follow Instructions**: The bootstrap document will tell you exactly which prompt file to read based on your assigned role, what constraints you must follow, and how you must reply.
3. **Execute**: Strictly follow the workflow defined in the bootstrap document.
