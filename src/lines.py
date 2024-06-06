import pygame
from movement import SmoothMovement, calculate_line_positions

class Line:
    def __init__(self, judgment_pos, angle, key_binding, movement):
        self.judgment_pos = judgment_pos
        self.angle = angle
        self.key_binding = key_binding
        self.notes = []
        self.movement = SmoothMovement(movement) if movement else None
        self.start_pos, self.end_pos = calculate_line_positions(judgment_pos, angle)

    def draw(self, screen):
        pygame.draw.line(screen, (255, 255, 255), self.start_pos, self.end_pos, 2)
        self.draw_judgment_circle(screen)

    def draw_judgment_circle(self, screen):
        pygame.draw.circle(screen, (255, 0, 0), (int(self.judgment_pos[0]), int(self.judgment_pos[1])), 10, 2)

    def add_note(self, note):
        self.notes.append(note)

    def update_notes(self, current_time):
        for note in self.notes:
            note.update(current_time, self.start_pos, self.end_pos, self.angle)
            if self.has_exceeded_judgment_point(note):
                self.notes.remove(note)

    def has_exceeded_judgment_point(self, note):
        # Calculate the distance from the note to the starting point
        traveled_distance = ((note.pos[0] - self.start_pos[0]) ** 2 + (note.pos[1] - self.start_pos[1]) ** 2) ** 0.5
        # Calculate the total distance the note should travel
        total_distance = ((self.start_pos[0] - self.judgment_pos[0]) ** 2 + (self.start_pos[1] - self.judgment_pos[1]) ** 2) ** 0.5
        return traveled_distance >= total_distance

    def update_position(self, current_time):
        if self.movement:
            new_pos, new_angle = self.movement.update(current_time)
            self.judgment_pos = new_pos
            self.angle = new_angle
            self.start_pos, self.end_pos = calculate_line_positions(new_pos, new_angle)
        else:
            self.start_pos, self.end_pos = calculate_line_positions(self.judgment_pos, self.angle)
