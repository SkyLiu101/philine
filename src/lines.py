import pygame
import math
from movement import SmoothMovement, calculate_line_positions

class Line:
    def __init__(self, judgment_pos, angle, key_binding, movement, opacity_changes, fps, note_size, fail_range, far_animation_frames, pure_animation_frames):
        self.judgment_pos = judgment_pos
        self.angle = angle
        self.key_binding = key_binding
        self.hold_notes = []
        self.notes = []
        self.movement = SmoothMovement(movement) if movement else None
        self.start_pos, self.end_pos = calculate_line_positions(judgment_pos, angle)
        self.fps = fps
        self.note_size = note_size
        self.iskeypressed = []
        self.fail_range = fail_range


        self.alpha = 0  # Initial opacity
        self.target_alpha = 255
        self.opacity_changes = sorted(opacity_changes, key=lambda x: x['time']) if opacity_changes else []

        self.far_animation_frames = far_animation_frames
        self.pure_animation_frames = pure_animation_frames
        self.animation_frames = self.far_animation_frames
        self.animation_index = 0
        self.animation_start_time = None
    
    def start_animation(self, frames):
        self.animation_frames = frames
        self.animation_index = 0
        self.animation_start_time = pygame.time.get_ticks()

    def update_animation(self, current_time):
        if self.animation_frames and self.animation_start_time:
            elapsed_time = current_time - self.animation_start_time
            frame_duration = 50  # Duration of each frame in milliseconds
            self.animation_index = (elapsed_time // frame_duration) % len(self.animation_frames)
            if elapsed_time > frame_duration * len(self.animation_frames):
                self.animation_index = 0


    def draw(self, screen):
        if self.alpha > 0:  # Only draw if the alpha value is greater than 0
            # Create a surface with alpha transparency
            line_surface = pygame.Surface((self.end_pos[0] - self.start_pos[0]+1, self.end_pos[1] - self.start_pos[1]+1), pygame.SRCALPHA)
            # Draw the line on the surface
            pygame.draw.line(line_surface, (255, 255, 255, min(self.alpha,255)), (0, 0), (self.end_pos[0] - self.start_pos[0], self.end_pos[1] - self.start_pos[1]), 2)
            # Blit the surface onto the screen at the start_pos location
            screen.blit(line_surface, self.start_pos)
        self.draw_key_binding(screen)

    def is_held(self):
        return self.iskeypressed
    def draw_key_binding(self, screen):
        if self.alpha > 0:  # Only draw if the alpha value is greater than 0
            font = pygame.font.SysFont(None, 36)
            total_width = 0
            key_texts = []
            
            # Render key texts and calculate total width
            for key in self.key_binding:
                key_text = font.render(pygame.key.name(key), True, (255, 255, 255, min(self.alpha, 255)))
                key_texts.append(key_text)
                total_width += key_text.get_width()
            
            # Add space between keys
            space_between_keys = 10
            total_width += space_between_keys * (len(self.key_binding) - 1)
            
            # Calculate starting x position for centering the text
            start_x = self.judgment_pos[0] - total_width // 2
            
            # Draw each key text
            for key_text in key_texts:
                key_text_rect = key_text.get_rect(midtop=(start_x, self.judgment_pos[1] + self.note_size[1]))
                screen.blit(key_text, key_text_rect)
                start_x += key_text.get_width() + space_between_keys
    
    def draw_animation(self, screen):
        if self.animation_frames:
            frame = pygame.transform.scale(self.animation_frames[int(self.animation_index)],self.note_size)
            rect = frame.get_rect(center=self.judgment_pos)
            screen.blit(frame, rect)

    def add_note(self, note):
        self.notes.append(note)

    def add_hold_note(self, note):
        self.hold_notes.append(note)

    def update_notes(self, current_time):
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

            
    def on_key_press(self,key):
        self.iskeypressed.append(key)

    def on_key_release(self,key):
        self.iskeypressed.remove(key)