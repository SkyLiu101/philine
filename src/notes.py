import pygame
import math

class Note:
    def __init__(self, judgment_pos, speed, hit_time):
        self.judgment_pos = judgment_pos
        self.speed = speed
        self.hit_time = hit_time
        self.spawn_time = self.calculate_spawn_time(judgment_pos, speed, hit_time)
        self.pos = list(judgment_pos)
        self.start_pos = None
        self.end_pos = None
        self.start_time = None

    def calculate_spawn_time(self, judgment_pos, speed, hit_time):
        distance = 600  # The distance from the spawn point to the judgment point; adjust as needed
        travel_time = distance / speed
        spawn_time = hit_time - travel_time * 1000  # Convert to milliseconds
        return spawn_time

    def update(self, current_time, line_start_pos, line_end_pos, line_angle):
        if current_time < self.spawn_time:
            return

        if self.start_time is None:
            self.start_time = current_time
        self.start_pos = line_start_pos
        self.end_pos = line_end_pos

        elapsed_time = (current_time - self.start_time) / 1000.0  # Time in seconds

        rad_angle = math.radians(line_angle)
        distance = self.speed * elapsed_time
        self.pos[0] = self.start_pos[0] + distance * math.cos(rad_angle)
        self.pos[1] = self.start_pos[1] + distance * math.sin(rad_angle)


    def draw(self, screen):
        if self.pos:
            pygame.draw.circle(screen, (255, 255, 255), (int(self.pos[0]), int(self.pos[1])), 5)
