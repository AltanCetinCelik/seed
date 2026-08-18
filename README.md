# Seed Agent OS

A local experimentation repository for agent orchestration, memory workflows, voice interfaces, and prototype operating-system patterns for AI-assisted tooling.

## What is included

- Agent runtime experiments and orchestration scripts
- Guardrails and approval flows for safe local actions
- Memory review and state-tracking prototypes
- Voice and presence-oriented AI interactions
- Research and system integration notes

## Scope

This repository is best understood as an experimental sandbox for exploring AI agent design, local tool orchestration, and operational safety patterns. It mixes research artifacts, UI experiments, and automation scripts instead of a single polished application.

## Getting started

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Then run the relevant scripts or gates you want to test.

## Common workflows

```bash
python seed_v75_gate.py
python seed_agent_hq_v30.py
python seed_dashboard_v106.py
```

## Security note

This project contains experimental local tooling and should be used in a controlled environment. Always review commands and permissions before executing automation or external integrations.

## Repository organization

- `seed_*.py` — agent runtime experiments
- `seed_research/` — research and analysis notes
- `Seed_Core.md` and related docs — design references and rules
- `requirements.txt` — Python dependencies
