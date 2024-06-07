import pygame
import math

class Note:
    
    def __init__(self, judgment_pos, speed, hit_time, image):
        self.judgment_pos = judgment_pos
        self.speed = speed
        self.hit_time = hit_time
        self.spawn_time = self.calculate_spawn_time(judgment_pos, speed, hit_time)
        self.pos = list(judgment_pos)
        self.start_pos = None
        self.end_pos = None
        self.start_time = None

        self.image = image
        self.is_held = False  # To track if the note is being held


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

        elapsed_time = (self.hit_time-current_time) / 1000.0  # Time in seconds
    
        rad_angle = math.radians(line_angle)
        distance = self.speed * elapsed_time
        self.pos[0] = self.end_pos[0] - distance * math.cos(rad_angle)
        self.pos[1] = self.end_pos[1] - distance * math.sin(rad_angle)


    def draw(self, screen):
        if self.pos:
            rect = self.image.get_rect(center=(int(self.pos[0]), int(self.pos[1])))
            screen.blit(self.image, rect)

class HoldNote(Note):
    def __init__(self, judgment_pos, speed, hit_time, head_image, mid_image, end_image, end_time):
        super().__init__(judgment_pos, speed, hit_time, head_image, note_type='hold', end_time=end_time)
        self.head_image = head_image
        self.mid_image = mid_image
        self.end_image = end_image

    def draw(self, screen, current_time, line_angle):
        if self.pos:
            # Draw the head
            head_rect = self.head_image.get_rect(center=(int(self.pos[0]), int(self.pos[1])))
            screen.blit(self.head_image, head_rect)

            # Calculate and draw the mid sections
            if current_time >= self.spawn_time and current_time <= self.end_time:
                elapsed_time = (current_time - self.spawn_time) / 1000.0  # Time in seconds
                rad_angle = math.radians(line_angle)
                mid_distance = self.speed * elapsed_time
                mid_pos = [self.start_pos[0] + mid_distance * math.cos(rad_angle),
                           self.start_pos[1] + mid_distance * math.sin(rad_angle)]
                mid_rect = self.mid_image.get_rect(center=(int(mid_pos[0]), int(mid_pos[1])))
                screen.blit(self.mid_image, mid_rect)

            # Draw the end
            if current_time >= self.end_time:
                end_rect = self.end_image.get_rect(center=(int(self.judgment_pos[0]), int(self.judgment_pos[1])))
                screen.blit(self.end_image, end_rect)