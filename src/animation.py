import pygame

def load_animation_frames():
    far_frames = []
    pure_frames = []
    for i in range(1, 9):  # Assuming frames are named sequentially from Far-1.png to Far-8.png
        frame = pygame.image.load(f'assets/Animations/Far-{i}.png').convert_alpha()
        far_frames.append(frame)
        frame = pygame.image.load(f'assets/Animations/Pure-{i}.png').convert_alpha()
        pure_frames.append(frame)
    return far_frames, pure_frames