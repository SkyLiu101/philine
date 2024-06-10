import pygame
import math
from movement import SmoothMovement, calculate_line_positions

class Line:
    def __init__(self, judgment_pos, angle, key_binding, movement, opacity_changes, fps, note_size, fail_range):
        self.judgment_pos = judgment_pos
        self.angle = angle
        self.key_binding = key_binding
        self.hold_notes = []
        self.notes = []
        self.movement = SmoothMovement(movement) if movement else None
        self.start_pos, self.end_pos = calculate_line_positions(judgment_pos, angle)
        self.fps = fps
        self.note_size = note_size
        self.ispressed = False
        self.fail_range = fail_range

        self.judgment_circle_radius = 10  # Initial radius
        self.judgment_circle_color = (255, 0, 0)  # Initial color (red)
        self.original_radius = 10
        self.original_color = (255, 0, 0)

        self.alpha = 0  # Initial opacity
        self.target_alpha = 255
        self.opacity_changes = sorted(opacity_changes, key=lambda x: x['time']) if opacity_changes else []

    def draw(self, screen):
        if self.alpha > 0:  # Only draw if the alpha value is greater than 0
            # Create a surface with alpha transparency
            line_surface = pygame.Surface((self.end_pos[0] - self.start_pos[0]+1, self.end_pos[1] - self.start_pos[1]+1), pygame.SRCALPHA)
            # Draw the line on the surface
            pygame.draw.line(line_surface, (255, 255, 255, min(self.alpha,255)), (0, 0), (self.end_pos[0] - self.start_pos[0], self.end_pos[1] - self.start_pos[1]), 2)
            # Blit the surface onto the screen at the start_pos location
            screen.blit(line_surface, self.start_pos)
        self.draw_judgment_circle(screen)
        self.draw_key_binding(screen)

    def draw_key_binding(self, screen):
        if self.alpha > 0:  # Only draw if the alpha value is greater than 0
            font = pygame.font.SysFont(None, 36)
            key_text = font.render(pygame.key.name(self.key_binding), True, (255, 255, 255, min(self.alpha,255)))
            key_text_rect = key_text.get_rect(center=(self.judgment_pos[0] + self.note_size[0] * math.cos(math.radians(self.angle)),
                                                      self.judgment_pos[1] + self.note_size[0] * math.sin(math.radians(self.angle))))
            screen.blit(key_text, key_text_rect)

    def draw_judgment_circle(self, screen):
        if self.alpha > 0:  # Only draw if the alpha value is greater than 0
            circle_surface = pygame.Surface((self.judgment_circle_radius * 2, self.judgment_circle_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(circle_surface, (*self.judgment_circle_color, min(255,self.alpha)), (self.judgment_circle_radius, self.judgment_circle_radius), self.judgment_circle_radius, 2)
            screen.blit(circle_surface, (int(self.judgment_pos[0] - self.judgment_circle_radius), int(self.judgment_pos[1] - self.judgment_circle_radius)))

    def add_note(self, note):
        self.notes.append(note)

    def add_hold_note(self, note):
        self.hold_notes.append(note)

    def update_notes(self, current_time, ispressed, judge_time,score):
        for hold_note in self.hold_notes:

            hold_note.update_surface(current_time, self.angle, self.end_pos)
            if hold_note.end_time <= current_time:
                self.hold_notes.remove(hold_note)
        for note in self.notes:
            note.update(current_time, self.start_pos, self.end_pos, self.angle)
            if self.has_exceeded_judgment_point(note):
                self.notes.remove(note)

    def has_exceeded_judgment_point(self, note):
        # Calculate the distance from the note to the starting point
        traveled_distance = ((note.pos[0] - self.start_pos[0]) ** 2 + (note.pos[1] - self.start_pos[1]) ** 2) ** 0.5
        # Calculate the total distance the note should travel
        total_distance = ((self.start_pos[0] - self.judgment_pos[0]) ** 2 + (self.start_pos[1] - self.judgment_pos[1]) ** 2) ** 0.5
        return traveled_distance >= total_distance + 20

    def update_position(self, current_time):
        if self.movement:
            new_pos, new_angle = self.movement.update(current_time)
            self.judgment_pos = new_pos
            self.angle = new_angle
            self.start_pos, self.end_pos = calculate_line_positions(new_pos, new_angle)
        else:
            self.start_pos, self.end_pos = calculate_line_positions(self.judgment_pos, self.angle)
        
        self.update_opacity(current_time)
    
    def update_opacity(self, current_time):
        if self.opacity_changes:
            for change in self.opacity_changes:
                self.target_alpha = change['opacity']
                self.target_time = change['time']
                if current_time < change['time']:
                    break
                

            if current_time < self.target_time:
                time_diff = self.target_time - current_time
                opacity_diff = self.target_alpha - self.alpha
                speed = opacity_diff / time_diff /self.fps*1000
                self.alpha += speed
            else:
                self.alpha = self.target_alpha

            
    def on_key_press(self):
        self.ispressed = True
        self.judgment_circle_radius += 1
        self.judgment_circle_color = (0, 255, 0)  # Change color to green

    def on_key_release(self):
        self.ispressed = False
        self.judgment_circle_radius = self.original_radius
        self.judgment_circle_color = self.original_color