import pygame

class Line:
    def __init__(self, start_pos, end_pos, key_binding, movement):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.key_binding = key_binding
        self.notes = []
        self.movement = movement
        self.current_movement_index = 0

    def draw(self, screen):
        pygame.draw.line(screen, (255, 255, 255), self.start_pos, self.end_pos, 2)

    def add_note(self, note):
        self.notes.append(note)

    def update_notes(self):
        for note in self.notes:
            note.update()
            if note.pos[1] > 600:
                self.notes.remove(note)

    def update_position(self, current_time):
        if self.current_movement_index < len(self.movement):
            movement_event = self.movement[self.current_movement_index]
            if current_time >= movement_event["time"]:
                new_pos = movement_event["new_pos"]
                delta_x = new_pos[0] - self.start_pos[0]
                delta_y = new_pos[1] - self.start_pos[1]
                self.start_pos[0] += delta_x
                self.end_pos[0] += delta_x
                self.start_pos[1] += delta_y
                self.end_pos[1] += delta_y
                self.current_movement_index += 1
