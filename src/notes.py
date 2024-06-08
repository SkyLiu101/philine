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
        self.opacity = 255

        self.image = image
        self.is_held = False  # To track if the note is being held


    def calculate_spawn_time(self, judgment_pos, speed, hit_time):
        distance = 3000  # The distance from the spawn point to the judgment point; adjust as needed
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


class HoldNote():
    def __init__(self, judgment_pos, speed, start_time, head_image, mid_image, end_image, end_time):
        self.speed = speed
        self.judgment_pos = judgment_pos
        self.start_time = start_time
        self.end_time = end_time
        self.head_image = head_image
        self.mid_image = mid_image
        self.end_image = end_image
        self.hold_note_segment = []
        self.failed = False
        self.fragment_notes()
    
    def fragment_notes(self):
        self.hold_note_segment.append(Note(self.judgment_pos, self.speed, self.start_time, self.head_image))

        density = (self.end_time - self.start_time) / (self.self.mid_image.height / self.speed)
        segment_time = self.start_time + density
        while segment_time < self.end_time:
            self.hold_note_segment.append(Note(self.judgment_pos, self.speed, segment_time, self.mid_image))
            segment_time = segment_time + density

        self.hold_note_segment.append(Note(self.judgment_pos, self.speed, self.end_time, self.end_image))


    def update(self, current_time, line_start_pos, line_end_pos, line_angle):
        for note in self.hold_note_segment:
            if current_time>note.hit_time:
                self.hold_note_segment.remove(note)
                continue
            note.update(current_time, line_start_pos, line_end_pos, line_angle)
        if not len(self.hold_note_segment):
            #score.append 1
            pass

    def draw(self, screen):
        for note in self.hold_note_segment:
            note.draw(screen)