import pygame

def load_animation_frames():
    far_frames = []
    pure_frames = []
    for i in range(0, 8):  # Assuming frames are named sequentially from Far-0.png to Far-7.png
        frame = pygame.image.load(f'assets/Animations/Touch_Effect_Far/Far-{i}.png').convert_alpha()
        far_frames.append(frame)
        frame = pygame.image.load(f'assets/Animations/Touch_Effect_Pure/Pure-{i}.png').convert_alpha()
        pure_frames.append(frame)
    print(len(far_frames), len(pure_frames))
    return far_frames, pure_frames

