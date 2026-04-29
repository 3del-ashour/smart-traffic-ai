# Smart Traffic AI — Master Project Plan

> **Read this first. Then read [INTEGRATION_CONTRACTS.md](docs/INTEGRATION_CONTRACTS.md). Then read your personal `docs/member-X-*.md` file.**

---

## 1. What We're Building

A **simulated 4-way intersection** where an AI agent watches traffic in real time and decides how long each traffic light should stay green to **minimize total wait time** for all cars. Instead of dumb fixed timers, our AI **thinks** and adapts.

### The Demo Story (7 minutes)
1. Show fixed timers — cars pile up unfairly.
2. Toggle AI mode — the agent reasons, optimizes, lights adapt.
3. Show live graph: average wait time **drops** as AI learns.
4. Show comparison plot: AI vs Fixed → AI wins.

---

## 2. The 3 Mandatory Pillars (from the assignment)

| Pillar | Our Implementation |
|--------|--------------------|
| **Logic** | Propositional Logic + Modus Ponens inference (`src/logic/`) |
| **Math of AI** | Linear Algebra (matrices, eigenvectors, L2 norms) + Probability (Poisson distribution, expected values) (`src/math_models/`) |
| **Optimization** | Simulated Annealing on green-light timings (`src/optimization/`) |

Plus: **Pygame UI** + **Monitoring & Evaluation** (AI vs Fixed comparison).

---

## 3. Architecture

```
                ┌───────────────────────┐
                │   Pygame UI Layer     │   ← Members 7 & 8
                │  (renderer + controls)│
                └──────────┬────────────┘
                           ▼
                ┌───────────────────────┐
                │   Traffic Agent       │   ← Member 2
                │   (rational agent)    │
                └──┬─────┬──────┬───────┘
                   │     │      │
        ┌──────────┘     │      └────────────┐
        ▼                ▼                   ▼
┌────────────┐  ┌──────────────┐    ┌────────────────┐
│Logic Engine│  │ Math Models  │    │  Optimization  │
│(Member 3)  │  │ (Member 4)   │    │   (Member 5)   │
└────────────┘  └──────────────┘    └────────────────┘
        ▲                ▲                   ▲
        └────────────────┼───────────────────┘
                ┌────────┴───────────┐
                │   Simulation Core  │  ← Member 6
                │ (intersection+cars)│
                └────────────────────┘
                         │
                ┌────────┴───────────┐
                │  Evaluation Layer  │  ← Member 9
                └────────────────────┘
```

---

## 4. Folder Structure

```
smart-traffic-ai/
├── README.md
├── PROJECT_PLAN.md
├── requirements.txt
├── main.py                       # Entry point
├── config.py                     # Shared types (everyone reads)
├── src/
│   ├── simulation/               # Member 6
│   ├── logic/                    # Member 3
│   ├── math_models/              # Member 4
│   ├── optimization/             # Member 5
│   ├── agent/                    # Member 2
│   ├── ui/                       # Members 7 & 8
│   └── evaluation/               # Member 9
├── tests/
└── docs/
    ├── INTEGRATION_CONTRACTS.md
    ├── member-1-project-manager.md
    └── ... (9 member docs)
```

---

## 5. Tech Stack

| Layer | Tool |
|-------|------|
| Language | Python 3.10+ |
| UI | Pygame |
| Math | NumPy |
| Plots | Matplotlib |
| Tests | Pytest |
| Style | Black + Flake8 |
| VCS | Git + GitHub |

---

## 6. The 9 Roles

| # | Role | Files |
|---|------|-------|
| 1 | Project Manager & Integration Lead | `main.py`, `README.md`, `requirements.txt`, repo settings |
| 2 | Lead Developer (Agent Architect) | `src/agent/traffic_agent.py` |
| 3 | Logic Engineer | `src/logic/rules.py`, `src/logic/inference.py` |
| 4 | Mathematical Modeler | `src/math_models/matrices.py`, `src/math_models/probability.py` |
| 5 | Optimization Specialist | `src/optimization/simulated_annealing.py` |
| 6 | Simulation Engineer | `src/simulation/intersection.py`, `vehicle.py`, `traffic_generator.py` |
| 7 | UI/UX — Renderer | `src/ui/renderer.py` |
| 8 | UI/UX — Controls | `src/ui/controls.py` |
| 9 | Evaluation & Monitoring | `src/evaluation/metrics.py`, `src/evaluation/monitor.py` |

> Each member has a personal `docs/member-X-*.md` with **step-by-step instructions, code skeletons, and a copy-paste AI prompt**.

---

## 7. The 10 Integration Rules (READ TWICE)

1. Don't change shared types in `config.py` without group approval.
2. Function signatures in `INTEGRATION_CONTRACTS.md` are **frozen**.
3. Imports must use absolute paths from `src/`.
4. Each module includes unit tests in `tests/`.
5. UI is read-only — never mutates simulation state directly.
6. Random seeds are configurable for reproducible demos.
7. Format with `black` before committing.
8. Every PR must pass `pytest`.
9. No `print()` debugging — use `logging`.
10. No hardcoded magic numbers — put them in `config.py`.

---

## 8. Git Workflow

1. Branch per member: `feature/<your-name>-<module>`
2. Never push to `main` directly.
3. Open Pull Requests — Project Manager reviews + merges.
4. Pull `main` daily before starting new work.
5. Commit small, commit often, write meaningful messages.
6. Never commit large binaries or secrets.

---

## 9. The 9-Day Crash Timeline

(See README.md for the full day-by-day breakdown.)

**Hard rule:** every member must push **something working** by **end of Day 4 (Fri 02 May)**. Integration depends on it.

---

## 10. Deliverables

1. **Project Report** — single document, all 9 names + roles on title page, comprehensive coverage of logic + math + optimization
2. **Live Demo** — 7 minutes max in class
3. **Backup Video** — uploaded to YouTube/Drive (link only)

**Deadline: 08.05.2025 — Friday 16:00**

---

## 11. Final Integration Checklist (Member 1 runs)

- [ ] `pytest` all tests pass
- [ ] `python main.py` runs without errors
- [ ] Both AI mode and Fixed-timer mode work
- [ ] Comparison shows AI is better
- [ ] Report has all 9 names + roles on title page
- [ ] Demo rehearsed under 7 minutes
- [ ] Backup video uploaded to YouTube
- [ ] Submission link prepared
