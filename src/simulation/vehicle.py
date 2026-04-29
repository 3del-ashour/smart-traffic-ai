"""Vehicle entity — owned by Member 6."""


class Vehicle:
    def __init__(self, direction, spawn_time):
        self.direction = direction
        self.spawn_time = spawn_time
        self.wait_time = 0.0
