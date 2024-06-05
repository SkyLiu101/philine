import pygame

class Line:
    def __init__(self, start_pos, end_pos, key_binding):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.key_binding = key_binding
        self.notes = []

    def draw(self, screen):
        pygame.draw.line(screen, (255, 255, 255), self.start_pos, self.end_pos, 2)

    def add_note(self, note):
        self.notes.append(note)

    def update_notes(self):
        for note in self.notes:
            note.update()
            if note.pos[1] > 600:
                self.notes.remove(note)
