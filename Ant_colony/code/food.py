import pygame
import random
import numpy as np


class Food(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.image = pygame.transform.scale(pygame.image.load(
            "aco/images/corn.png").convert_alpha(), (32//4, 32//4))
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
        self.angle = random.uniform(0, 2 * np.pi)
        self.taken = False

    def draw(self, screen):
        self.rotate_image = pygame.transform.rotate(
            self.image, np.degrees(self.angle))
        screen.blit(self.rotate_image, self.rect)
