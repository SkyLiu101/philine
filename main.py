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
    screen_width, screen_height = 800, 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    illustration_path = chart['illustration_path']
    background_path = config['score_image']

    font = pygame.font.Font(None, 36)

    # Colors
    background = pygame.image.load(background_path)
    background = pygame.transform.scale(background, (config['screen_width'], config['screen_height']))

    text_color = (0, 0, 0)  # Green text

    # Load illustration and scale it
    illustration = pygame.image.load(illustration_path)
    illustration = pygame.transform.scale(illustration, (300, 300))

    # Main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                running = False

        
        screen.blit(background, (0, 0))

        # Draw the illustration
        screen.blit(illustration, (50, 50))

        # Rank and score information
        rank_label = font.render("Rank", True, text_color)
        screen.blit(rank_label, (400, 50))

        acquired_score_label = font.render("Acquired score", True, text_color)
        acquired_score_value = font.render(f"{score.score}", True, text_color)
        screen.blit(acquired_score_label, (150, 400))
        screen.blit(acquired_score_value, (350, 400))

        previous_high_score_label = font.render("Previous high score", True, text_color)
        previous_high_score_value = font.render(f"{chart['previous_high_score']}", True, text_color)
        screen.blit(previous_high_score_label, (150, 450))
        screen.blit(previous_high_score_value, (350, 450))

        # Pure, Far, and Lost count
        pure_count_label = font.render("Pure count", True, text_color)
        pure_count_value = font.render(f"{score['pure_count']}", True, text_color)
        screen.blit(pure_count_label, (150, 500))
        screen.blit(pure_count_value, (350, 500))

        far_count_label = font.render("Far count", True, text_color)
        far_count_value = font.render(f"{score['far_count']}", True, text_color)
        screen.blit(far_count_label, (150, 550))
        screen.blit(far_count_value, (350, 550))

        lost_count_label = font.render("Lost count", True, text_color)
        lost_count_value = font.render(f"{score['lost_count']}", True, text_color)
        screen.blit(lost_count_label, (150, 600))
        screen.blit(lost_count_value, (350, 600))

        pygame.display.flip()

    pygame.quit()

def load_chart(chart_path):
    with open(chart_path, 'r') as file:
        return json.load(file)

# Load configuration
config = load_config('config/config.json')
chart_path = 'charts/tutorial.json'
chart = load_chart(chart_path)

# Initialize Pygame 
screen = pygame.display.set_mode((config['screen_width'], config['screen_height']), pygame.NOFRAME)

pygame.init()

# Initialize and run the game
#game = Game(screen, 'charts/tutorial.json', config, 0) 
#score = game.run()

score = Score(chart, None)

show_score(screen, score, chart, config)

pygame.quit()
sys.exit()
