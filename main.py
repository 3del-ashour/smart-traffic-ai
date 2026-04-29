"""
Entry point for Smart Traffic AI.
Wires Intersection + Agent + Renderer + Controls + Monitor.
"""
import pygame
from config import SIMULATION_FPS, TimingPlan, Direction
from src.simulation.intersection import Intersection
from src.agent.traffic_agent import TrafficAgent
from src.ui.renderer import Renderer
from src.ui.controls import Controls
from src.evaluation.monitor import Monitor


FIXED_PLAN = TimingPlan(durations={d: 30 for d in Direction})


def main():
    pygame.init()
    pygame.font.init()

    intersection = Intersection()
    agent = TrafficAgent()
    renderer = Renderer()
    controls = Controls()
    monitor = Monitor()
    font = pygame.font.SysFont("Arial", 18)

    clock = pygame.time.Clock()
    running = True

    while running:
        dt = clock.tick(SIMULATION_FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            controls.handle_event(event)

        if controls.reset_requested:
            intersection = Intersection()
            agent = TrafficAgent()
            monitor = Monitor()
            controls.reset_requested = False

        if not controls.paused:
            state = intersection.step(dt)

            if intersection.cycle_complete():
                if controls.ai_mode:
                    plan = agent.act(state)
                    intersection.apply_timing(plan)
                else:
                    intersection.apply_timing(FIXED_PLAN)

            monitor.record(state)

        renderer.draw(intersection.get_state())
        controls.draw(renderer.screen, font)
        pygame.display.flip()

    pygame.quit()
    monitor.save_report("docs/metrics_log.csv")


if __name__ == "__main__":
    main()
