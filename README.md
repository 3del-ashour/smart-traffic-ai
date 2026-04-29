# Smart Traffic AI 🚦

An AI-powered Smart Traffic Light Controller built as a group project for the **Principles of AI** course.

The agent perceives traffic density at a 4-way intersection, reasons with **logical inference**, models the world with **linear algebra and probability**, and uses **Simulated Annealing** to optimize green-light timings — minimizing total wait time across all lanes.

---

## 📋 Project Plan
👉 [Read the full plan](PROJECT_PLAN.md)

## 📜 Integration Contracts (READ BEFORE CODING)
👉 [INTEGRATION_CONTRACTS.md](docs/INTEGRATION_CONTRACTS.md)

---

## 👥 Team Members & Roles

| # | Name | Role | Personal Plan |
|---|------|------|---------------|
| 1 | _name_ | Project Manager & Integration Lead | [docs](docs/member-1-project-manager.md) |
| 2 | _name_ | Lead Developer (Agent Architect) | [docs](docs/member-2-lead-developer.md) |
| 3 | _name_ | Logic Engineer | [docs](docs/member-3-logic-engineer.md) |
| 4 | _name_ | Mathematical Modeler | [docs](docs/member-4-math-modeler.md) |
| 5 | _name_ | Optimization Specialist | [docs](docs/member-5-optimization.md) |
| 6 | _name_ | Simulation Engineer | [docs](docs/member-6-simulation.md) |
| 7 | _name_ | UI/UX — Renderer | [docs](docs/member-7-renderer.md) |
| 8 | _name_ | UI/UX — Controls & Dashboard | [docs](docs/member-8-controls.md) |
| 9 | _name_ | Evaluation & Monitoring | [docs](docs/member-9-evaluation.md) |

---

## 🧠 The 3 AI Pillars

| Pillar | Implementation |
|--------|----------------|
| **Logic** | Propositional Logic + Modus Ponens inference engine |
| **Math of AI** | Linear Algebra (matrices, eigenvectors, L2 norms) + Probability (Poisson distribution, expected values) |
| **Optimization** | Simulated Annealing on green-light durations |

---

## 🏗️ Architecture

```
                ┌───────────────────────┐
                │   Pygame UI Layer     │
                │  (renderer + controls)│
                └──────────┬────────────┘
                           ▼
                ┌───────────────────────┐
                │   Traffic Agent       │
                │   (rational agent)    │
                └──┬─────┬──────┬───────┘
                   │     │      │
        ┌──────────┘     │      └────────────┐
        ▼                ▼                   ▼
┌────────────┐  ┌──────────────┐    ┌────────────────┐
│Logic Engine│  │ Math Models  │    │  Optimization  │
└────────────┘  └──────────────┘    └────────────────┘
        ▲                ▲                   ▲
        └────────────────┼───────────────────┘
                ┌────────┴───────────┐
                │   Simulation Core  │
                │ (intersection+cars)│
                └────────────────────┘
```

---

## 📁 Folder Structure

```
smart-traffic-ai/
├── README.md
├── PROJECT_PLAN.md
├── requirements.txt
├── main.py
├── config.py
├── src/
│   ├── simulation/      # Member 6
│   ├── logic/           # Member 3
│   ├── math_models/     # Member 4
│   ├── optimization/    # Member 5
│   ├── agent/           # Member 2
│   ├── ui/              # Members 7 & 8
│   └── evaluation/      # Member 9
├── tests/
└── docs/
```

---

## 🚀 Setup

### Prerequisites
- Python 3.10+
- Git

### Install & Run
```bash
git clone https://github.com/<owner>/smart-traffic-ai.git
cd smart-traffic-ai
pip install -r requirements.txt
python main.py
```

### Run Tests
```bash
pytest
```

---

## 🌿 Git Workflow (Everyone Follows This)

1. **Never push to `main` directly.**
2. Create your own branch:
   ```bash
   git checkout -b feature/<your-name>-<module>
   ```
3. Commit small and often with clear messages:
   ```bash
   git commit -m "feat(logic): add modus ponens engine"
   ```
4. Push your branch:
   ```bash
   git push origin feature/<your-name>-<module>
   ```
5. Open a **Pull Request** on GitHub → Project Manager reviews → merge.
6. Pull `main` daily before starting new work:
   ```bash
   git pull origin main
   ```

---

## ✅ Contribution Rules

- ✅ Follow function signatures in [`INTEGRATION_CONTRACTS.md`](docs/INTEGRATION_CONTRACTS.md) **exactly**.
- ✅ Add unit tests for your module under `tests/`.
- ✅ Format code with `black` before committing.
- ✅ Keep commits scoped to your module.
- ❌ Never modify `config.py` shared types without group approval.
- ❌ Never commit large binaries or secrets.
- ❌ No `print()` debugging in final code — use `logging`.

---

## 🛠️ Tech Stack

| Layer | Tool |
|-------|------|
| Language | Python 3.10+ |
| UI / Animation | Pygame |
| Math | NumPy |
| Plots | Matplotlib |
| Tests | Pytest |
| Style | Black + Flake8 |

---

## 📅 Timeline

| Week | Focus | Output |
|------|-------|--------|
| Week 1 | Setup + module skeletons | Empty classes with correct signatures |
| Week 2 | Implementation | Each module fully working + tests pass |
| Week 3 | Integration + report + demo | Full demo, comparison study, video |

---

## 🎯 Deliverables

1. **Project Report** — single document, all 9 names + roles on title page
2. **Live Demo** — 7 minutes, in class
3. **Backup Video** — uploaded to YouTube/Drive (link only)

---

## 📆 Deadline

**08.05.2025 — Friday 16:00**

---

## 📬 Communication

- **GitHub Issues** — task tracking + technical questions
- **Group Chat** — daily updates
- **Weekly Stand-up** — every [day/time]

---

> Built with ❤️ by 9 students for the Principles of AI course.
