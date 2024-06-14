import pygame
import math
from animation import load_animation_frames

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
        self.opacity = 255
        self.image = image
        self.is_held = False  # To track if the note is being held

    def calculate_spawn_time(self, judgment_pos, speed, hit_time):
        distance =3200  # The distance from the spawn point to the judgment point; adjust as needed
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

        elapsed_time = (self.hit_time - current_time) / 1000.0  # Time in seconds

        rad_angle = math.radians(line_angle)
        distance = self.speed * elapsed_time
        self.pos[0] = self.end_pos[0] - distance * math.cos(rad_angle)
        self.pos[1] = self.end_pos[1] - distance * math.sin(rad_angle)

    def draw(self, screen, line_angle):
        if self.pos:
            rotated_image = pygame.transform.rotate(self.image, 90 - line_angle)
            rect = rotated_image.get_rect(center=(int(self.pos[0]), int(self.pos[1])))
            screen.blit(rotated_image, rect)


class HoldNote:
    def __init__(self, judgment_pos, speed, start_time, head_image, mid_image, end_image, end_time, note_size, checkpoint_data, line):
        self.speed = speed
        self.judgment_pos = judgment_pos
        self.start_time = start_time
        self.end_time = end_time
        self.head_image = pygame.transform.scale(head_image, note_size)
        self.mid_image = pygame.transform.scale(mid_image, note_size)
        self.end_image = pygame.transform.scale(end_image, note_size)
        self.note_size = note_size
        self.surface = None
        self.dimmed_surface = None
        self.surface_endpos = judgment_pos
        self.spawn_time = self.calculate_spawn_time(judgment_pos, speed)
        self.judged = False
        self.held = True
        self.head_note = Note(judgment_pos, speed, start_time, head_image)
        self.total_length = self.speed * (self.end_time - self.start_time) / 1000
        self.dimmed_alpha = 128
        self.checkpoint_data = sorted(checkpoint_data, key=lambda x: x['time']) if checkpoint_data else []
        self.line = line
        self.istouch = False

    def calculate_spawn_time(self, judgment_pos, speed):
        distance = 3200  # The distance from the spawn point to the judgment point; adjust as needed
        travel_time = distance / speed
        spawn_time = self.start_time - travel_time * 1000  # Convert to milliseconds
        return spawn_time

    def create_surface(self):
        mid_length = self.total_length - self.note_size[1]  # Subtract the head and tail heights
        if mid_length < 0:
            mid_length = 0

        # Create surface
        width = self.note_size[0]
        height = int(self.total_length)
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)

        # Blit stretched mid
        stretched_mid = pygame.transform.scale(self.mid_image, (self.note_size[0], int(mid_length)))
        mid_rect = stretched_mid.get_rect(midtop=(width // 2, 0))
        self.surface.blit(stretched_mid, mid_rect)

        # Blit tail
        tail_rect = self.end_image.get_rect(midtop=(width // 2,int(mid_length)))
        
        self.surface.blit(self.end_image, tail_rect)

    def update_surface(self, current_time, line_angle, line_end_pos):
        if self.surface is None:
            self.create_surface()

        if current_time > self.start_time:
            self.istouch = True

        remaining_time = (self.end_time - current_time) / 1000.0  # Time in seconds
        total_distance = self.speed * remaining_time 

        # Update the surface length to reflect the distance traveled
        surface_height = self.surface.get_height()
        current_length = min(surface_height, total_distance)

        if current_length > 0:
            temp_surface = pygame.Surface((self.note_size[0], int(current_length)), pygame.SRCALPHA)
            temp_surface.blit(self.surface, (0, 0), (0, surface_height - int(current_length), self.note_size[0], int(current_length)))
            self.surface = temp_surface
        
        self.head_note.update(current_time, self.judgment_pos, line_end_pos, line_angle)

    def draw(self, screen, line_angle, current_time, line_end_pos):

        if self.surface:
            # Rotate the surface according to the line angle
            self.dimmed_surface = self.surface.copy()
            self.dimmed_surface.set_alpha(self.dimmed_alpha)
            if self.line.is_held() or not self.istouch:
                rotated_surface = pygame.transform.rotate(self.surface, 90-line_angle)
            else:
                rotated_surface = pygame.transform.rotate(self.dimmed_surface, 90-line_angle)
            rotated_surface = pygame.transform.flip(rotated_surface,flip_x=True,flip_y=True)

            # Calculate the position to blit the rotated surface
            rad_angle = math.radians(line_angle)
            distance_remaining = self.speed * (self.end_time-current_time) / 1000 /2 
            if current_time < self.start_time:
                distance_remaining = distance_remaining + self.speed * (self.start_time - current_time) /1000
            if distance_remaining > 0:
                offset_x = line_end_pos[0] - (distance_remaining) * math.cos(rad_angle)
                offset_y = line_end_pos[1] - (distance_remaining) * math.sin(rad_angle)
                rotated_rect = rotated_surface.get_rect(center=(int(offset_x), int(offset_y)))

                self.head_note.pos = [
                    offset_x + (self.total_length)* math.cos(rad_angle)/2,
                    offset_y + (self.total_length)* math.sin(rad_angle)/2
                    ]
                if current_time > self.start_time:
                    self.head_note.pos = line_end_pos

                # Draw the outline for debugging
                # pygame.draw.rect(rotated_surface, (255, 0, 0), rotated_surface.get_rect(), 1)
                self.head_note.draw(screen, line_angle)

                screen.blit(rotated_surface, rotated_rect.topleft)
