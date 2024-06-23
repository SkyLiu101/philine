import sys
import os
import pygame
import json


# Add the src directory to the system path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config import load_config
from game import Game
from score import Score

def show_score(screen, score, chart, config):
    pygame.init()
    screen_width, screen_height = config['screen_width'], config['screen_height']
    screen = pygame.display.set_mode((screen_width, screen_height))
    illustration_path = chart['illustration_path']
    background_path = config['score_image']

    font = pygame.font.Font('assets/fonts/exo-regular.ttf', 74)
    currscore_font = pygame.font.Font('assets/fonts/exo-light.ttf', 74)
    prevscore_font = pygame.font.Font('assets/fonts/exo-regular.ttf', 74)

    # Colors
    background = pygame.image.load(background_path)
    background = pygame.transform.scale(background, (config['screen_width'], config['screen_height']))

    text_color = (0, 0, 0)  # Green text
    score_color = (255,255,255)

    # Load illustration and scale it
    illustration = pygame.image.load(illustration_path)
    illustration = pygame.transform.scale(illustration, (360, 360))

    scoreval = int(score.score)

    # Main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                running = False

        
        screen.blit(background, (0, 0))

        # Draw the illustration
        screen.blit(illustration, (216, 77))

        # Rank and score information
        ranks = config['rank_paths']
        if score.score >= 10000000:
            rank_label_path = ranks['Pure_Memory']
        elif score.score >= 92000000:
            rank_label_path = ranks['S']
        elif score.score >= 82000000:
            rank_label_path = ranks['A']
        elif score.score >= 65000000:
            rank_label_path = ranks['B']
        else:
            rank_label_path = ranks['F']

        rank_label = pygame.image.load(rank_label_path)
        rank_label = pygame.transform.scale(rank_label, (452, 360))
        screen.blit(rank_label, (216, 524))


        res_background_path = config['result_bg']
        res_background = rank_label = pygame.image.load(res_background_path)
        res_background = pygame.transform.scale(res_background, (595, 293))
        screen.blit(res_background, (818, 171))

        formatted_score = f"{scoreval:08d}"  # Ensure score is at least 8 digits with leading zeros
        # Add apostrophes as thousands separators
        parts = [formatted_score[max(i - 3, 0):i] for i in range(len(formatted_score), 0, -3)]
        formatted_score_with_apostrophes = "'".join(reversed(parts))
        score_text = currscore_font.render(f"{formatted_score_with_apostrophes}", True, (score_color))
        screen.blit(score_text, (900, 180))

        previous_high_score_label = font.render("Previous high score", True, text_color)
        previous_high_score_value = font.render(f"{chart['previous_highscore']}", True, text_color)
        screen.blit(previous_high_score_label, (150, 450))
        screen.blit(previous_high_score_value, (350, 450))

        # Pure, Far, and Lost count
        pure_count_label = font.render("Pure", True, text_color)
        pure_count_value = font.render(f"{score.pure_cnt+score.extra_pure_cnt} + {score.extra_pure_cnt}", True, text_color)
        screen.blit(pure_count_label, (150, 500))
        screen.blit(pure_count_value, (350, 500))

        far_count_label = font.render("Far", True, text_color)
        far_count_value = font.render(f"{score.far_cnt}", True, text_color)
        screen.blit(far_count_label, (150, 550))
        screen.blit(far_count_value, (350, 550))

        lost_count_label = font.render("bad", True, text_color)
        lost_count_value = font.render(f"{score.bad_cnt}", True, text_color)
        screen.blit(lost_count_label, (150, 600))
        screen.blit(lost_count_value, (350, 600))

        lost_count_label = font.render("miss", True, text_color)
        lost_count_value = font.render(f"{score.miss_cnt}", True, text_color)
        screen.blit(lost_count_label, (150, 650))
        screen.blit(lost_count_value, (350, 650))

        pygame.display.flip()

    pygame.quit()

def load_chart(chart_path):
    with open(chart_path, 'r') as file:
        return json.load(file)

# Load configuration
config = load_config('config/config.json')
chart_path = 'charts/testify.json'
chart = load_chart(chart_path)

# Initialize Pygame 
screen = pygame.display.set_mode((config['screen_width'], config['screen_height']), pygame.NOFRAME)

pygame.init()

game = Game(screen, chart_path, config, 0) 
score = game.run()

#score = Score(chart, None)

show_score(screen, score, chart, config)

pygame.quit()
sys.exit()
