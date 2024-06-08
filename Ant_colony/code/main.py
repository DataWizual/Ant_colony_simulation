import pygame
import random
from settings import *
from ant import Ant
from pheromone import Pheromone
from food import Food
from quadtree import *


class Setup:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Ant colony')
        icon = pygame.image.load('aco/images/ant_ico.png')
        pygame.display.set_icon(icon)
        surf = pygame.transform.scale(pygame.image.load(
            "aco/images/corn.png").convert_alpha(), (32/2, 32/2))
        cursor = pygame.cursors.Cursor((0, 0), surf)
        pygame.mouse.set_cursor(cursor)
        self.clock = pygame.time.Clock()
        self.delta_time = self.clock.tick(FPS)

    def draw_nest(self):
        nest = pygame.transform.scale(pygame.image.load(
            "aco/images/nest.png").convert_alpha(), (32*3, 32*3))
        nest_rect = nest.get_rect(center=(NEST_X, NEST_Y))
        self.screen.blit(nest, nest_rect)
        return nest_rect

    def create_objects(self):
        self.ants = pygame.sprite.Group(
            [Ant(self.delta_time) for _ in range(ANTS)])
        self.leader_ants = pygame.sprite.Group(
            [Ant(self.delta_time) for _ in range(LEADER_ANTS)])
        self.foods = pygame.sprite.Group(
            [Food(random.randint(1000, WIDTH-100),
                  random.randint(600, HEIGHT-100)) for _ in range(1000)])
        # self.foods = pygame.sprite.Group(
        #     [Food(random.randint(0, WIDTH),
        #           random.randint(0, HEIGHT)) for _ in range(1000)])
        self.pheromones = pygame.sprite.Group()

    def pheromone_quadtree(self):
        pheromone_boundary = Rectangle(0, 0, WIDTH, HEIGHT)
        self.pheromone_qtree = Quadtree(pheromone_boundary, 1)

    def user_event(self):
        self.add_pheromone = pygame.USEREVENT
        pygame.time.set_timer(self.add_pheromone, 100)

    def type_of_ants(self, ant_type, nest):
        for ant in ant_type:
            ant.update(self.screen, nest, self.foods,
                       self.ant_quad_tree, self.pheromone_qtree)
            ant.draw(self.screen)
            # self.ant_quad_tree.draw(self.screen)
            x, y = ant.ant_coord()
            if ant.dragged_food:
                ant.dragged_food.rect.center = (x, y)

    def main(self):
        self.create_objects()
        self.pheromone_quadtree()
        self.user_event()

        while True:
            self.screen.fill(SAND)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    food = Food(*mouse_pos)
                    self.foods.add(food)
                if len(self.pheromones) <= 2000:
                    if event.type == self.add_pheromone:
                        for leader_ant in self.leader_ants:
                            pheromone = Pheromone(
                                int(leader_ant.x), int(leader_ant.y), lifespan, self.pheromone_qtree)
                            self.pheromones.add(pheromone)

            for pheromone in self.pheromones:
                pheromone.update(self.pheromone_qtree)
                pheromone.draw(self.screen)
                # pheromone_qtree.draw(screen)

            nest = self.draw_nest()

            for food in self.foods:
                food.draw(self.screen)

            ant_boundary = Rectangle(0, 0, WIDTH, HEIGHT)
            self.ant_quad_tree = Quadtree(ant_boundary, 1)

            self.type_of_ants(self.ants, nest)
            self.type_of_ants(self.leader_ants, nest)

            pygame.display.update()
            self.clock.tick(FPS)


if __name__ == '__main__':
    setup_instance = Setup()
    setup_instance.main()
