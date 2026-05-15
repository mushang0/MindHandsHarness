# 快速开始

这份文档演示一次完整的 MindHandsHarness mission。

## 1. 检查 Harness 状态

```bash
python3 .harness/bin/harness.py status
python3 .harness/bin/harness.py doctor
```

干净状态下应看到：

```text
Active Session: None
Active Mission: None
Active Stage:   idle
Spec Status:    missing
OK! All checks passed.
```

## 2. 启动 Mission

```bash
python3 .harness/bin/harness.py start "Implement the requested feature"
```

这会创建：

- active session ID。
- active mission ID。
- `.harness/runtime/current/mission.json`。
- `.harness/sessions/` 下的 session event。

## 3. 派发 Reader

Reader 任务应该窄、具体、可验证。

```bash
python3 .harness/bin/harness.py dispatch-role \
  --role Reader \
  --objective "Find the files and behavior relevant to the requested feature" \
  --questions "Which files own this behavior?; What exact insertion points matter?; What default behavior must not change?; What unknowns remain?"
```

打印 Worker 启动指令：

```bash
python3 .harness/bin/harness.py worker-instructions
```

打开新的 agent 窗口，粘贴打印出来的指令。

## 4. 收集 Reader 结果

Worker 回复 `Completed.` 后运行：

```bash
python3 .harness/bin/harness.py collect-role --role Reader
```

Coordinator 接下来判断证据是否充分。如果不充分，继续派发更窄的问题给 Reader。

## 5. 创建并校验 Spec

```bash
python3 .harness/bin/harness.py write-spec
```

编辑：

```text
.harness/runtime/current/implementation_spec.md
```

Spec 应包含：

- Objective。
- Scope。
- Required Changes。
- Evidence References。
- Allowed Autonomy。
- Must Not Decide。
- Stop Conditions。

校验并冻结版本快照：

```bash
python3 .harness/bin/harness.py spec-check
```

成功后会创建：

```text
.harness/runtime/current/specs/implementation_spec.v001.md
```

## 6. 派发 Coder

```bash
python3 .harness/bin/harness.py dispatch-role \
  --role Coder \
  --objective "Implement the checked implementation spec"
```

再次打印 Worker 指令：

```bash
python3 .harness/bin/harness.py worker-instructions
```

打开新的 Worker 窗口运行 Coder。

## 7. 收集、验证、审查

```bash
python3 .harness/bin/harness.py collect-role --role Coder
```

高风险变更建议继续派发 Tester 和 Reviewer：

```bash
python3 .harness/bin/harness.py dispatch-role \
  --role Tester \
  --objective "Verify the implementation against the checked spec"

python3 .harness/bin/harness.py dispatch-role \
  --role Reviewer \
  --objective "Audit the diff for spec compliance and scope violations"
```

## 8. 归档

任务完成后：

```bash
python3 .harness/bin/harness.py archive-current
```

归档会保留：

- Mission metadata。
- Mission state。
- 每个 task 的 prompt 和 result。
- 版本化 specs。
- Session event 引用。

