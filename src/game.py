import pygame
import json
from lines import Line
from notes import Note
from clock import GameClock

class Game:
    def __init__(self, screen, chart_path, config):
        self.screen = screen
        self.config = config
        self.lines = []
        self.notes = []
        self.score = 0
        self.load_chart(chart_path)
        self.clock = GameClock(config['fps'])
        self.chart_finished = False

    def load_chart(self, chart_path):
        with open(chart_path, 'r') as file:
            chart_data = json.load(file)
        
        # Convert key_bindings values to actual Pygame key constants
        key_bindings = {k: getattr(pygame, v) for k, v in self.config['key_bindings'].items()}
        
        for line_data in chart_data['lines']:
            key_binding = line_data['key_binding']
            if key_binding not in key_bindings:
                raise KeyError(f"Key binding '{key_binding}' not found in config key_bindings.")
            self.lines.append(Line(
                judgment_pos=line_data['judgment_pos'],
                angle=line_data['angle'],
                key_binding=key_bindings[key_binding],
                movement=line_data.get('movement', [])
            ))
        self.note_data = chart_data['notes']

        pygame.mixer.init()
        self.audio_path = chart_data['audio_path']
        pygame.mixer.music.load(self.audio_path)

    def check_collision(self, current_time, key, line):
        if key == line.key_binding and line.notes:
            # Check for note collision here 
            if abs(current_time - line.notes[0].hit_time) < self.config['extra_pure_threshold']:
                # Extra perfect hit
                return '3'
            if abs(current_time - line.notes[0].hit_time) < self.config['pure_threshold']:
                # Perfect hit
                return '2'
            elif abs(current_time - line.notes[0].hit_time) < self.config['far_threshold']:
                # Far hit
                return '1'
            elif abs(current_time - line.notes[0].hit_time) < self.config['bad_threshold']:
                # Bad hit
                return '-2'
            pass

    def display_score(self):
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (1200, 10))

    def display_time_elapsed(self, current_time):
        font = pygame.font.SysFont(None, 36)
        # Calculate displayed time
        currentTimeConverted = current_time / 1000
        currMin = int(currentTimeConverted / 60)
        currSec = int(currentTimeConverted - (currMin * 60))
        # Concat into string
        displayedTime = ""
        if currMin == 0:
            displayedTime = f"Time: {currSec} sec"
        else:
            displayedTime = f"Time: {currMin} min {currSec} sec"
        time_text = font.render(displayedTime, True, (255, 255, 255))
        self.screen.blit(time_text, (10, 10))


    def run(self):
        running = True

        pygame.mixer.music.play()

        start_time = pygame.time.get_ticks()

        while running:
            current_time = pygame.time.get_ticks() - start_time

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    for line in self.lines:
                        status = self.check_collision(current_time, event.key, line)
                        if status:
                            line.notes.remove(line.notes[0])
                            self.score = self.score + int(status)
                            print(status)

            # Check if it's time to add a new note
            for note_data in self.note_data:
                if 'spawned' not in note_data:
                    line_index = note_data['line']
                    hit_time = note_data['hit_time']
                    judgment_pos = self.lines[line_index].judgment_pos
                    note_speed = self.config['note_speed']*note_data['speed']
                    note = Note(judgment_pos, note_speed, hit_time)
                    if current_time >= note.spawn_time:
                        self.lines[line_index].add_note(note)
                        note_data['spawned'] = True  # Mark the note as spawned
            
            # Update line positions based on movement data
            for line in self.lines:
                line.update_position(current_time)
                line.update_notes(current_time)

            # Check if audio had stop playing
            if not pygame.mixer.music.get_busy():
                self.chart_finished = True

            if self.chart_finished:
                running = False

            self.screen.fill((0, 0, 0))
            
            for line in self.lines:
                line.draw(self.screen)
                for note in line.notes:
                    note.draw(self.screen)
            self.display_time_elapsed(current_time)
            self.display_score()
            pygame.display.flip()
            self.clock.tick()

        pygame.quit()
        sys.exit()
