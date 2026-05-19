# Harness Boot Context

## Project Identity
MindHandsHarness is a context-gated Coordinator/Executor harness for long-running AI software work.

## Current Architecture
- Entry Router: `AGENTS.md`
- Project Context System: `.harness/context/` and `.harness/memory/`
- Coordinator Runtime: `.harness/roles/coordinator.md` plus `harness context boot`
- Executor Runtime: `.harness/roles/executor.md` plus task packets
- Harness Runtime: `.harness/bin/harness.py`

## Core Rule
Coordinator decides. Executor acts. Scripts manage state.

## Must Load
- `AGENTS.md`
- this boot file
- `python3 .harness/bin/harness.py context boot`
- current role file

## Load On Demand
- project map: when locating files
- context-loading policy: when deciding how much to read
- rtk policy: when reading source, logs, generated files, or command output
- memory policy: when applying memory
- skill policy and registry: when a task benefits from an external skill

## Do Not Load By Default
- full source files
- full logs
- generated artifacts
- archived sessions
- task `logs/` directories

## Handoff Goal
A fresh Coordinator should understand current state from this file, `context boot`, project map, and memory without rereading old conversations.
