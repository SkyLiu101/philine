import pygame
import json
import sys
import os
from lines import Line
from notes import Note, HoldNote
from score import Score
from clock import GameClock
from animation import load_animation_frames
import pygame.transform


class Game:
    def __init__(self, screen, chart_path, config, start_time, autoplay):
        self.screen = screen
        self.chart_path = chart_path
        self.config = config
        self.lines = []
        self.notes = []
        self.score = None
        self.far_animation_frames, self.pure_animation_frames = load_animation_frames()
        self.load_chart(chart_path)
        self.clock = GameClock(config['fps'])
        self.chart_finished = False
        self.paused = False
        self.start_time = start_time
        self.current_time = start_time
        self.isautoplay = autoplay

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
        self.pause_sound = pygame.mixer.Sound('assets/sounds/pause.wav')
        self.illustration = pygame.transform.scale(self.illustration, (config['screen_width'], config['screen_width'])).convert_alpha()


        self.quit_button = pygame.Rect(10, 10, 80, 40)
        self.quit_button_color = (255, 0, 0)
        self.quit_button_text = pygame.font.SysFont(None, 24).render('Quit', True, (255, 255, 255))

        self.restart_button = pygame.Rect(10, 60, 80, 40)
        self.restart_button_color = (0, 255, 0)
        self.restart_button_text = pygame.font.SysFont(None, 24).render('Restart', True, (255, 255, 255))
    
    def restart(self):
        self.__init__(self.screen, self.chart_path, self.config, self.start_time, self.isautoplay)
        self.run()

    def load_illustration(self, illustration_path):
        """Load the dimmed illustration image"""
        illustration_filename = os.path.basename(illustration_path)
        dimmed_path = os.path.join('assets/dim', illustration_filename)
        self.illustration = pygame.image.load(dimmed_path).convert()
        self.illustration = pygame.transform.scale(self.illustration, (self.config['screen_width'], self.config['screen_height']))
        return self.illustration

    def play_hit_sound(self):
        self.hit_sound.play()
    def play_pause_sound(self):
        self.pause_sound.play()

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
        
        self.illustration = self.load_illustration(chart_data['illustration_path'])

        pygame.mixer.init()
        self.audio_path = chart_data['audio_path']
        self.offset = chart_data['offset']
        pygame.mixer.music.load(self.audio_path)

    def closest_note(self, line):

        ret_note = line.notes[0]

        for note in line.notes:
            if note.hit_time<ret_note.hit_time:
                ret_note = note
                pass

        return ret_note
    
    def get_current_time(self):
        return self.current_time / 1000.0  # return time in seconds

    def pause(self):
        self.paused = True
        pygame.mixer.music.pause()
        self.play_pause_sound()

    def resume(self):
        self.paused = False
        pygame.mixer.music.unpause()

    def toggle_pause(self):
        if self.paused:
            self.resume()
        else:
            self.pause()
    

    def draw_buttons(self):
        # Draw quit button
        pygame.draw.rect(self.screen, self.quit_button_color, self.quit_button)
        self.screen.blit(self.quit_button_text, (self.quit_button.x + 10, self.quit_button.y + 10))
        
        # Draw restart button
        pygame.draw.rect(self.screen, self.restart_button_color, self.restart_button)
        self.screen.blit(self.restart_button_text, (self.restart_button.x + 10, self.restart_button.y + 10))
    def create_blurred_surface(self):
        surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        surface.blit(self.screen, (0, 0))

        scale_factor = 0.1
        small_surface = pygame.transform.smoothscale(surface, (int(self.screen.get_width() * scale_factor), int(self.screen.get_height() * scale_factor)))
        blurred_surface = pygame.transform.smoothscale(small_surface, self.screen.get_size())

        dim_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        dim_surface.fill((0, 0, 0, 128))

        blurred_surface.blit(dim_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        return blurred_surface

    def check_collision(self, current_time, note, line):
        # Check for note collision here 
        if abs(current_time - note.hit_time) < self.config['extra_pure_threshold']:
            # Extra perfect hit
            self.score.update_score('extra_pure')
            line.start_animation(line.pure_animation_frames)
            return '3'
        if abs(current_time - note.hit_time) < self.config['pure_threshold'] and not self.isautoplay:
            # Perfect hit
            self.score.update_score('pure')
            line.start_animation(line.pure_animation_frames)
            return '2'
        elif abs(current_time - note.hit_time) < self.config['far_threshold'] and not self.isautoplay:
            # Far hit
            self.score.update_score('far')
            line.start_animation(line.far_animation_frames)
            return '1'
        elif abs(current_time - note.hit_time) < self.config['bad_threshold'] and not self.isautoplay:
            self.score.update_score('bad')
            # Bad hit   
            # Add a fade function here
            # summon a red note on the deleted note, and fade out just like phigros. fade time should be stored in config.
            # ...

            # the real note will be deleted out side of the collision func, do not repeatingly delete.
            return '-2'
        pass
    def display_score(self):
        running = True
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
        music_played = False

        current_time = self.start_time*1000
        start_time = pygame.time.get_ticks() - current_time

        if self.isautoplay:
            for line in self.lines:
                line.on_key_press(0)


        while running:
            if not music_played:
                if current_time > self.offset:
                    pygame.mixer.music.play(start=self.start_time)
                    music_played = True
            if self.paused:
                start_time = pygame.time.get_ticks() - current_time
            current_time = pygame.time.get_ticks() - start_time
            self.current_time = current_time


            if self.isautoplay:
                for line in self.lines:
                    for note in line.notes:
                        status = self.check_collision(current_time, note, line)
                        if status:
                            line.notes.remove(note)

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.toggle_pause()
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    for line in self.lines:
                        if event.key in line.key_binding:
                            for note in line.notes:
                                if self.paused or self.isautoplay:
                                    continue
                                status = self.check_collision(current_time, note, line)
                                if status:
                                    line.notes.remove(note)
                                    break
                            line.on_key_press(event.key)
                elif event.type == pygame.KEYUP:
                    for line in self.lines:
                        if event.key in line.key_binding and not self.isautoplay:
                            line.on_key_release(event.key)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.paused:
                        if self.quit_button.collidepoint(event.pos):
                            running = False
                        elif self.restart_button.collidepoint(event.pos):
                            self.restart()

            for line in self.lines:
                for hold_note in line.hold_notes:
                        while hold_note.checkpoint_data:
                            if current_time < hold_note.checkpoint_data[0]['time']:
                                break
                            if hold_note.line.is_held() or self.isautoplay:
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
                    hold_note = HoldNote(judgment_pos, hold_note_speed, hit_time, self.note_images[f'{note_type}_hold_head'], self.note_images[f'{note_type}_hold_mid'], self.note_images[f'{note_type}_hold_end'], end_time, note_size, checkpoint_data, self.lines[line_index])
                    if current_time >= hold_note.spawn_time:
                        self.lines[line_index].add_hold_note(hold_note)
                        self.hold_note_data.remove(hold_note_data)  # Mark the note as spawned

            
            # Update line positions based on movement data
            for line in self.lines:
                if self.paused:
                    continue
                line.update_animation(current_time)
                line.update_position(current_time)
                line.update_notes(current_time)
                if line.notes:
                    note = self.closest_note(line)
                    if current_time > note.hit_time + self.config['far_threshold']:
                        line.notes.remove(note)
                        if not self.isautoplay:
                            self.score.update_score('miss')
                        else:
                            self.score.update_score('extra_pure')

            # Check if audio had stop playing
            if not pygame.mixer.music.get_busy() and not self.paused and music_played: 
                self.chart_finished = True

            if self.chart_finished:
                running = False

            self.screen.blit(self.illustration, (0, 0))  # Draw the background illustration
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

            if self.paused:
                blurred_surface = self.create_blurred_surface()
                self.screen.blit(blurred_surface, (0, 0))
                font = pygame.font.Font(None, 74)
                paused_text = font.render("▶️▶️", True, (255, 255, 255))
                paused_rect = paused_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
                self.screen.blit(paused_text, paused_rect)
                self.draw_buttons()

            pygame.display.flip()
            if not self.paused:
                self.clock.tick()

        return self.score
