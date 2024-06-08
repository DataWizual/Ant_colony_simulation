import pygame
import random
import numpy as np
from settings import *
from quadtree import *


class Ant(pygame.sprite.Sprite):
    def __init__(self, delta_time=1):
        super().__init__()
        self.delta_time = delta_time
        self.speed = 0.3 * delta_time
        self.index = 0
        self.size = (IMAGE_W/3, IMAGE_H/3)
        self.move = [pygame.transform.scale(pygame.image.load(
            f'aco/images/ant{i}.png').convert_alpha(), self.size) for i in range(1, 9)]
        self.x = NEST_X
        self.y = NEST_Y
        self.image = self.move[self.index]
        self.rect = self.image.get_rect()
        self.angle = random.uniform(0, 2*np.pi)
        self.choose = 0
        self.encountered_pheromones = set()
        self.encountered_foods = set()
        self.dragged_food = None

    def update(self, screen, nest, foods, ant_quad_tree, pheromone_qtree):
        self.speedx = self.speed * np.cos(self.angle)
        self.speedy = -self.speed * np.sin(self.angle)

        self.x += self.speedx
        self.y += self.speedy

        self.image = self.move[self.index//2]
        if self.index < 15:
            self.index += 1
        else:
            self.index = 0

        self.collision(ant_quad_tree)

        self.wrap_around()

        self.image, self.rect = self.rotate_center()

        if self.choose == 0:
            self.search_for_food(screen, foods, pheromone_qtree)
        elif self.choose == 1:
            self.return_to_nest(screen, nest, pheromone_qtree)

    def wrap_around(self):
        if self.x < 15:
            angel_d = self.angle_direction(-0.25, 0.25)
            self.angle += angel_d * 0.1
        elif self.x >= WIDTH-15:
            angel_d = self.angle_direction(0.75, 1.25)
            self.angle += angel_d * 0.1
        elif self.y < 15:
            angel_d = self.angle_direction(1.25, 1.75)
            self.angle += angel_d * 0.1
        elif self.y >= HEIGHT-15:
            angel_d = self.angle_direction(0.25, 0.75)
            self.angle += angel_d * 0.1

    def angle_direction(self, start, end):
        angle_dir = random.uniform(start * np.pi, end * np.pi)
        angle_direct = self.angle_different(angle_dir)
        return angle_direct

    def angle_different(self, direction):
        angle_diff = (direction - self.angle +
                      np.pi) % (2 * np.pi) - np.pi
        return angle_diff

    def draw_view(self, angle):  # , screen, color
        self.center_x, self.center_y = self.rect.center
        rect_center_x = self.center_x + 25 * np.cos(self.angle + angle)
        rect_center_y = self.center_y - 25 * np.sin(self.angle + angle)
        visible_range = Circle(rect_center_x, rect_center_y, 10, 10)
        # pygame.draw.circle(screen, color, (visible_range.x,
        #                                    visible_range.y), visible_range.w, 1)
        return visible_range

    def search_for_food(self, screen, foods, pheromone_qtree):
        dist_list = []
        for j in range(3):
            visible_range = self.draw_view(ANGLES[j])  # screen, COLORS[j],
            found = pheromone_qtree.query(visible_range)
            if found:
                untaken_foods = list(set(
                    food for food in foods if not food.taken))
                if untaken_foods:
                    random_food = random.choice(untaken_foods)
                    for f in found:
                        # pygame.draw.circle(screen, BLUE, (f.x, f.y), 3)
                        points = (f.x, f.y)
                        goal = [(random_food.x, random_food.y)]
                        dist_to = self.get_closest_point(points, goal)
                        dist_list.append((f.x, f.y, dist_to))
                        found.clear()
        if dist_list:
            angle_f = self.min_dist(dist_list)
            angel_d = self.angle_different(angle_f)
            self.angle += angel_d * 0.1
            dist_list.clear()
        self.take_food(foods)

    def take_food(self, foods):
        f_collisions = pygame.sprite.spritecollide(self, foods, False)
        if f_collisions:
            for food in f_collisions:
                if food not in self.encountered_foods and not food.taken:
                    self.dragged_food = food
                    self.encountered_foods.add(self.dragged_food)
                    self.angle += np.pi
                    food.taken = True
                    self.choose = 1
                    break

    def return_to_nest(self, screen, nest, pheromone_qtree):
        dist_list = []
        for j in range(3):
            visible_range = self.draw_view(ANGLES[j])  # screen, COLORS[j],
            found = pheromone_qtree.query(visible_range)
            if found:
                for f in found:
                    # pygame.draw.circle(screen, RED, (f.x, f.y), 3)
                    points = (f.x, f.y)
                    goal = (NEST_X, NEST_Y)
                    dist_to = self.get_closest_point(points, goal)
                    dist_list.append((f.x, f.y, dist_to))
                    found.clear()
        if dist_list:
            angle_f = self.min_dist(dist_list)
            angel_d = self.angle_different(angle_f)
            self.angle += angel_d * 0.1
            dist_list.clear()
        self.drop_food_in_nest(nest)

    def drop_food_in_nest(self, nest):
        if self.rect.colliderect(nest):
            if self.dragged_food is not None:
                self.dragged_food.kill()
                self.dragged_food = None
                self.angle += np.pi
            self.choose = 0

    def rotate_center(self):
        self.rotate_image = pygame.transform.rotate(
            self.image, np.degrees(self.angle))
        self.rotate_rect = self.rotate_image.get_rect(center=self.rect.center)
        return self.rotate_image, self.rotate_rect

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        # pygame.draw.rect(screen, (255, 0, 0), self.rect, 1)
        self.rect.center = (self.x, self.y)

    def ant_coord(self):
        self.food_center_x = self.x + DISTANCE * \
            np.cos(self.angle)
        self.food_center_y = self.y - DISTANCE * \
            np.sin(self.angle)
        return self.food_center_x, self.food_center_y

    def get_closest_point(self, points, goal):
        p1 = np.array(points)
        p2 = np.array(goal)
        dist_to = np.linalg.norm(p1 - p2)
        return dist_to

    def min_dist(self, dist):
        min_distance = min(dist, key=lambda x: x[2])
        min_p_x, min_p_y, _ = min_distance
        angle_calc = self.arctan_calc(min_p_x, min_p_y)
        angle_f = np.pi/2 - angle_calc
        return angle_f

    def arctan_calc(self, x, y):
        angle = np.arctan2(x - self.x, self.y - y)
        return angle

    def intersects(self, other):
        return self.rect.colliderect(other.rect)

    def update_angle(self):
        self.angle += random.uniform(-6 * np.pi / 180, 6 * np.pi / 180)

    def collision(self, ant_quad_tree):
        point_p = Point(self.x, self.y, self)
        ant_quad_tree.insert(point_p)
        range_area = Rectangle(
            self.rect.x, self.rect.y, self.rect.w, self.rect.h)
        ant_found = ant_quad_tree.query(range_area)
        if ant_found:
            for f in ant_found:
                other_ant = f.userdata
                if self != other_ant and\
                        self.intersects(other_ant):
                    self.update_angle()
                    other_ant.update_angle()
