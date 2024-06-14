import sys
import os
import pygame


# Add the src directory to the system path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config import load_config
from game import Game



# Load configuration
config = load_config('config/config.json')

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((config['screen_width'], config['screen_height']), pygame.NOFRAME)

# Initialize and run the game
game = Game(screen, 'charts/chart.json', config)
game.run()

pygame.quit()
sys.exit()
