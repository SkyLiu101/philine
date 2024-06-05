import pygame

class Note:
    def __init__(self, pos, speed):
        self.pos = list(pos)
        self.speed = speed

    def update(self):
        self.pos[1] += self.speed

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 255, 255), self.pos, 5)
