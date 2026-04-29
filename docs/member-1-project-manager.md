# Member 1 — Project Manager & Integration Lead

> **Read [PROJECT_PLAN.md](../PROJECT_PLAN.md) and [INTEGRATION_CONTRACTS.md](INTEGRATION_CONTRACTS.md) first.**

## Role
Coordinator. Repo owner. Integration tester. Report compiler. Demo director.

## You Own
- Repo settings (branch protection, PR rules)
- `README.md`, `requirements.txt`, `main.py`
- Final report compilation
- Daily stand-ups + integration testing

---

## Step-by-Step Plan

### Day 1 (Tue 29 Apr) — Setup
1. Create folder structure exactly as in `PROJECT_PLAN.md` Section 4.
2. Add `requirements.txt`:
   ```
   pygame>=2.5.0
   numpy>=1.24.0
   matplotlib>=3.7.0
   pytest>=7.4.0
   black>=23.0.0
   flake8>=6.0.0
   ```
3. Confirm `config.py` matches `INTEGRATION_CONTRACTS.md` exactly.
4. Open 9 GitHub Issues — one per member with their tasks as a checklist.
5. Set branch protection on `main`.

### Day 2-4 (Wed-Fri) — Coordinate
- Run a short stand-up every morning.
- Review every PR within 4 hours.
- Reject PRs that violate contracts.

### Day 5-6 (Sat-Sun) — Integration Lead
- Wire all modules in `main.py`.
- Run end-to-end tests.
- Help debug contract mismatches.

### Day 7-9 (Mon-Wed) — Report Director
Compile the final report with these sections:
1. Title page (all 9 names + roles)
2. Introduction & objective
3. System architecture (insert the diagram)
4. Logic chapter (Member 3 writes draft)
5. Math chapter (Member 4 writes draft)
6. Optimization chapter (Member 5 writes draft)
7. UI/UX chapter (Members 7, 8 write draft)
8. Evaluation results (Member 9 writes draft)
9. Conclusion + screenshots

### Day 10 (Thu 08 May) — Submit before 16:00

---

## `main.py` — You Write This

```python
# main.py
import pygame
from config import SIMULATION_FPS
from src.simulation.intersection import Intersection
from src.agent.traffic_agent import TrafficAgent
from src.ui.renderer import Renderer
from src.ui.controls import Controls
from src.evaluation.monitor import Monitor

def main():
    pygame.init()
    intersection = Intersection()
    agent = TrafficAgent()
    renderer = Renderer()
    controls = Controls()
    monitor = Monitor()

    clock = pygame.time.Clock()
    running = True
    while running:
        dt = clock.tick(SIMULATION_FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            controls.handle_event(event)

        if not controls.paused:
            state = intersection.step(dt)
            if intersection.cycle_complete() and controls.ai_mode:
                plan = agent.act(state)
                intersection.apply_timing(plan)
            monitor.record(state)

        renderer.draw(intersection.get_state())
        pygame.display.flip()

    pygame.quit()
    monitor.save_report("docs/metrics_log.csv")

if __name__ == "__main__":
    main()
```

---

## Best Practices
- Code review **everything** — even short PRs.
- Reject PRs that break a contract.
- Run `pytest` before merging.
- Keep an `INTEGRATION.md` log of any contract changes.

---

## AI Prompt You Can Paste

> "I'm the Project Manager for a Python AI Traffic Controller group project. The plan is in PROJECT_PLAN.md and the contracts are in INTEGRATION_CONTRACTS.md. Help me set up `main.py` that wires Intersection, TrafficAgent, Renderer, Controls, and Monitor according to the contracts. Also help me write `requirements.txt` and a strong `README.md`."
