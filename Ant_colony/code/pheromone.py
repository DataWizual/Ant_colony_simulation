import pygame
from settings import *
from quadtree import *


class Pheromone(pygame.sprite.Sprite):
    def __init__(self, x, y, lifespan, pheromone_qtree):
        super().__init__()
        self.x = x
        self.y = y
        self.lifespan = lifespan
        self.base_size = (2, 2)
        self.image = pygame.Surface(self.base_size, pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.point = Point(self.x, self.y)
        pheromone_qtree.insert(self.point)

    def update(self, pheromone_qtree):
        self.lifespan -= 1
        if self.lifespan <= 0:
            pheromone_qtree.delete_point(self.point)
            self.kill()

    def draw(self, screen):
        pygame.draw.circle(
            self.image, (84, 149, 232, 255), (1, 1), 3)
        self.rect.center = (self.x, self.y)
        screen.blit(self.image, self.rect)
