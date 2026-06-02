# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

列车晚点智能调度系统 (Train Delay Intelligent Rescheduling System) — an intelligent railway dispatching agent that uses multiple control algorithms (feedback control, ILC, RMPC) combined with fuzzy logic to generate rescheduling commands when train delays occur.

## Commands

```bash
# Interactive mode — parse natural language delay reports via LLM
python run.py

# Run built-in test cases
python run.py --test

# Quick start with dependency check
python start.py

# Create database tables
python -c "from database.create_tables import *"

# Install dependencies
pip install -r requirements.txt
```

## Architecture

The system follows a **two-phase pipeline**:

### Phase 1: NLP Parsing
`main.py` → `tools/nlp_parser_tool.py`

Natural language input (e.g., "C2503次列车在北京南站因设备故障晚点5分钟") is sent to an LLM (Qwen-Turbo via DashScope) which extracts structured JSON: `{train_number, station_name, delay_duration, delay_reason, is_urgent}`.

### Phase 2: Delay Processing & Control
`main.py` → `services/delay_service.py` → `algorithms/rescheduler.py`

The core rescheduling formula is: **u = g·x_current + f·x_previous_next**, where:
- `g = -(p+q) / [p+q+(c-1)²]` (current train gain)
- `f = (q+c·p) / [p+q+(c-1)²]` (previous train influence)
- Parameter `c` comes from **fuzzy logic** based on time-of-day passenger flow (`tools/fuzzy_passenger_flow.py`), falling back to the `feedback` table, then a default of 1.0.
- Parameters `p`, `q` are stored in the `feedback` table.

### Decision Engine (Alternative Path)
`services/decision_engine.py` provides a higher-level strategy selector based on dispatcher intent:
- **Urgent keywords** ("紧急", "迅速", etc.) → Feedback control
- **Passenger surge keywords** ("客流突变", etc.) → ILC (Iterative Learning Control)
- **Default** → RMPC (Robust Model Predictive Control)

If `fuzzy_membership_functions` table has no rows, it falls back to pure RMPC without fuzzy rules.

### Three Control Algorithms

| Algorithm | File | Description |
|-----------|------|-------------|
| Rescheduler (core) | `algorithms/rescheduler.py` | Uses the u = g·x + f·x formula based on delay propagation |
| ILC | `algorithms/ilc_controller.py` | Iterative learning control using previous batch's control rate and state error; solves via predicted gain matrix H1 |
| RMPC | `algorithms/rmpc_controller.py` | Robust MPC using LMI constraints solved via CVXPY (SCS solver); minimizes `a` subject to semidefinite constraints |

### Index Mapping System

The railway operates on a **closed-loop circular line** with 8 stations per circle and 15 physical trains. Two parallel index systems exist:

1. **Physical/DB IDs** (`train_id`, `station_id`): Auto-increment primary keys in MySQL
2. **Logical IDs** (`logic_train_id`, `logic_station_index`): Matrix indices for the control algorithms

Key mapping logic in `tools/index_mapper.py`:
- Train mapping: Each physical train `k` (1-15) has 6 train numbers (C2501-C2530, C2531-C2560, C2561-C2590)
- Odd train numbers = down direction, even = up direction
- `J_global = (k-1) * 8 + relative_j` where k is the circle number

`tools/logical_id_calculator.py` provides an older logical ID system (used as fallback).

### Database Layer

- **ORM**: SQLAlchemy with PyMySQL connecting to MySQL `train_dispatch`
- **Config**: `config/database.py` — hardcoded credentials (local dev)
- **Session factory**: `SessionLocal` — each service/function opens and closes its own session

Key tables: `trains`, `stations`, `delay_records` (with logical index columns), `dispatch_records`, `feedback` (p, q, c params), `fuzzy_membership_functions` (time-based passenger flow membership).

### LangChain Integration

The project uses LangChain for tool definitions (`langchain_core.tools.Tool`) but **not** for agent orchestration. The dispatch agent (`agent/dispatch_agent.py`) is a simple wrapper (`SimpleDispatchAgent`) that calls the NLP parser and decision tool sequentially — no LangChain agent executor is used.

## Key Patterns

- Each service function manages its own DB session (no shared sessions or connection pooling beyond SQLAlchemy defaults)
- LLM is configured via `config/llm_config.py` using DashScope's `qwen-turbo` model (API key is hardcoded — do not commit changes that expose it)
- The `tools/` directory contains LangChain Tool wrappers that accept JSON string input and return JSON string output
- Test files (`test_*.py`) are standalone scripts, not pytest-based
