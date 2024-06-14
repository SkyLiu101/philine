import pygame
import json
from lines import Line
from notes import Note, HoldNote
from score import Score
from clock import GameClock
from animation import load_animation_frames

class Game:
    def __init__(self, screen, chart_path, config):
        self.screen = screen
        self.config = config
        self.lines = []
        self.notes = []
        self.score = None
        self.far_animation_frames, self.pure_animation_frames = load_animation_frames()
        self.load_chart(chart_path)
        self.clock = GameClock(config['fps'])
        self.chart_finished = False

        self.note_size = tuple(config['note_size'])
        self.note_images = {
            'blue': pygame.transform.scale(pygame.image.load(config['note_images']['blue']).convert_alpha(), self.note_size),
            'orange': pygame.transform.scale(pygame.image.load(config['note_images']['orange']).convert_alpha(), self.note_size),
            'purple': pygame.transform.scale(pygame.image.load(config['note_images']['purple']).convert_alpha(), self.note_size),
            'blue_hold_head': pygame.transform.scale(pygame.image.load(config['note_images']['blue_hold_head']).convert_alpha(),self. note_size),
            'blue_hold_mid': pygame.transform.scale(pygame.image.load(config['note_images']['blue_hold_mid']).convert_alpha(), self.note_size),
            'blue_hold_end': pygame.transform.scale(pygame.image.load(config['note_images']['blue_hold_end']).convert_alpha(), self.note_size),
            'orange_hold_head': pygame.transform.scale(pygame.image.load(config['note_images']['orange_hold_head']).convert_alpha(), self.note_size),
            'orange_hold_mid': pygame.transform.scale(pygame.image.load(config['note_images']['orange_hold_mid']).convert_alpha(), self.note_size),
            'orange_hold_end': pygame.transform.scale(pygame.image.load(config['note_images']['orange_hold_end']).convert_alpha(), self.note_size),
            'purple_hold_head': pygame.transform.scale(pygame.image.load(config['note_images']['purple_hold_head']).convert_alpha(), self.note_size),
            'purple_hold_mid': pygame.transform.scale(pygame.image.load(config['note_images']['purple_hold_mid']).convert_alpha(), self.note_size),
            'purple_hold_end': pygame.transform.scale(pygame.image.load(config['note_images']['purple_hold_end']).convert_alpha(), self.note_size)
        }
        self.hit_sound = pygame.mixer.Sound('assets/sounds/tap.wav')
    def play_hit_sound(self):
        self.hit_sound.play()
    def load_chart(self, chart_path):
        with open(chart_path, 'r') as file:
            chart_data = json.load(file)
            self.score = Score(chart_data, self.play_hit_sound)
        
        # Convert key_bindings values to actual Pygame key constants
        key_bindings = {k: getattr(pygame, v) for k, v in self.config['key_bindings'].items()}
        
        for line_data in chart_data['lines']:
            key_binding = line_data['key_binding']
            for index in range(len(key_binding)):
                key_binding[index] = key_bindings[key_binding[index]]
            self.lines.append(Line(
                judgment_pos=line_data['judgment_pos'],
                angle=line_data['angle'],
                key_binding = key_binding,
                movement=line_data.get('movement', []),
                opacity_changes=line_data.get('opacity_changes', []),
                fps=self.config['fps'],
                note_size=self.config['note_size'],
                fail_range = self.config['far_threshold'],
                far_animation_frames=self.far_animation_frames,
                pure_animation_frames=self.pure_animation_frames
            ))
        self.note_data = chart_data['notes']
        if 'hold_notes' in chart_data:
            self.hold_note_data = chart_data['hold_notes']

        pygame.mixer.init()
        self.audio_path = chart_data['audio_path']
        pygame.mixer.music.load(self.audio_path)

    def closest_note(self, line):

        ret_note = line.notes[0]

        for note in line.notes:
            if note.hit_time<ret_note.hit_time:
                ret_note = note
                pass

        return ret_note

    def check_collision(self, current_time, note, line):
        # Check for note collision here 
        if abs(current_time - note.hit_time) < self.config['extra_pure_threshold']:
            # Extra perfect hit
            self.score.update_score('extra_pure')
            line.start_animation(line.pure_animation_frames)
            return '3'
        if abs(current_time - note.hit_time) < self.config['pure_threshold']:
            # Perfect hit
            self.score.update_score('pure')
            line.start_animation(line.pure_animation_frames)
            return '2'
        elif abs(current_time - note.hit_time) < self.config['far_threshold']:
            # Far hit
            self.score.update_score('far')
            line.start_animation(line.far_animation_frames)
            return '1'
        elif abs(current_time - note.hit_time) < self.config['bad_threshold']:
            # Bad hit   
            # Add a fade function here
            # summon a red note on the deleted note, and fade out just like phigros. fade time should be stored in config.
            # ...

            # the real note will be deleted out side of the collision func, do not repeatingly delete.
            return '-2'
        pass
    def display_score(self):

        font = pygame.font.Font('assets/fonts/Pixel.ttf',50)
        score = self.score.get_score()
        formatted_score = f"{score:08d}"  # Ensure score is at least 8 digits with leading zeros
        # Add apostrophes as thousands separators
        parts = [formatted_score[max(i - 3, 0):i] for i in range(len(formatted_score), 0, -3)]
        formatted_score_with_apostrophes = "'".join(reversed(parts))
        score_text = font.render(f"{formatted_score_with_apostrophes}", True, (255, 255, 255))
        self.screen.blit(score_text, (1150, 20))

    def display_time_elapsed(self, current_time):
        font = pygame.font.Font('assets/fonts/Pixel.ttf',50)
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
            current_time = (pygame.time.get_ticks() - start_time)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    for line in self.lines:
                        if event.key in line.key_binding:
                            for note in line.notes:
                                status = self.check_collision(current_time, note, line)
                                if status:
                                    line.notes.remove(note)
                            line.on_key_press(event.key)
                elif event.type == pygame.KEYUP:
                    for line in self.lines:
                        if event.key in line.key_binding:
                            line.on_key_release(event.key)

            for line in self.lines:
                for hold_note in line.hold_notes:
                        if hold_note.checkpoint_data:
                            if current_time >= hold_note.checkpoint_data[0]['time']:
                                if hold_note.line.is_held():
                                    self.score.update_score('extra_pure')
                                hold_note.checkpoint_data.remove(hold_note.checkpoint_data[0])
            
            for note_data in self.note_data:
                if 'spawned' not in note_data:
                    line_index = note_data['line']
                    hit_time = note_data['hit_time']
                    judgment_pos = self.lines[line_index].judgment_pos
                    note_speed = self.config['note_speed']*note_data['speed']
                    note_type = note_data.get('type', 'blue')  # Default to type_1 if not specified
                    note = Note(judgment_pos, note_speed, hit_time, self.note_images[f'{note_type}'])
                    if current_time >= note.spawn_time:
                        self.lines[line_index].add_note(note)
                        note_data['spawned'] = True  # Mark the note as spawned

            for hold_note_data in self.hold_note_data:
                if 'spawned' not in self.hold_note_data:
                    line_index = hold_note_data['line']
                    hit_time = hold_note_data['hit_time']
                    judgment_pos = self.lines[line_index].judgment_pos
                    hold_note_speed = self.config['note_speed']*hold_note_data['speed']
                    note_type = hold_note_data.get('type', 'blue')  # Default to type_1 if not specified
                    end_time = hold_note_data['end_time']
                    note_size = self.config['note_size']
                    checkpoint_data = []
                    for checkpoint in hold_note_data['checkpoints']:
                        checkpoint_data.append(checkpoint)
                    hold_note = HoldNote(judgment_pos, hold_note_speed, hit_time, self.note_images[f'{note_type}_hold_head'], self.note_images[f'{note_type}_hold_mid'], self.note_images[f'{note_type}_hold_end'], end_time, note_size, checkpoint_data, line)
                    if current_time >= hold_note.spawn_time:
                        self.lines[line_index].add_hold_note(hold_note)
                        self.hold_note_data.remove(hold_note_data)  # Mark the note as spawned

            
            # Update line positions based on movement data
            for line in self.lines:
                line.update_animation(current_time)
                line.update_position(current_time)
                line.update_notes(current_time)
                if line.notes:
                    note = self.closest_note(line)
                    if current_time > note.hit_time + self.config['far_threshold']:
                        line.notes.remove(note)

            # Check if audio had stop playing
            if not pygame.mixer.music.get_busy():
                self.chart_finished = True

            if self.chart_finished:
                running = False

            self.screen.fill((0, 0, 0, 255))
            
            # Draw lines and notes with proper blending
            for line in self.lines:
                line.draw(self.screen)
                line.draw_animation(self.screen)
                for hold_note in line.hold_notes:
                    hold_note.draw(self.screen, line.angle, current_time, line.end_pos)
                for note in line.notes:
                    note.draw(self.screen, line.angle)

            self.display_time_elapsed(current_time)
            self.display_score()
            pygame.display.flip()
            self.clock.tick()

        pygame.quit()
        sys.exit()
