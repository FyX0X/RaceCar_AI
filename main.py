import time
import pygame
import os
import numpy as np
import math
import keyboard

pygame.init()

WIN_WIDTH, WIN_HEIGHT = 600, 600
FPS = 30

RACE_TRACK_IMG = pygame.image.load(os.path.join("imgs", "race_track.png"))
CAR_IMG = pygame.transform.scale_by(pygame.image.load(os.path.join("imgs", "red_car.png")), 0.8)


class Car:
    IMG = CAR_IMG

    def __init__(self, pos):
        self.pos = np.array([float(pos[0]), float(pos[1])])  # 2d vector
        self.vel = np.zeros(2)  # 2d vector
        self.speed = 0  # scalar speed
        self.acceleration = np.zeros(2)  # 2d vector
        self.direction_vector = np.array([1, 0])
        self.rotation = 180  # scalar angle

        self.engine_max_force = 200  # change value later
        self.drag_coef = 0.005
        self.friction_coef = self.drag_coef * 30
        #self.friction_coef = 0.3  # change value later    friction is approx 30x drag
        self.mass = 0.5

        self.img_rect = None
        self.rotated_img = None

    def move(self, gas: float = 0, turn: float = 0, delta_time: float = 1 / FPS, time = 0):
        # calculate speed
        self.speed = math.sqrt(self.vel[0] ** 2 + self.vel[1] ** 2)  # scalar speed

        if self.speed != 0:
            self.direction_vector = self.vel / self.speed

        # calculate rotation
        self.rotation = math.degrees(math.atan2(self.direction_vector[0], -self.direction_vector[1])) - 90  # rotation from direction vector

        # calculate acceleration
        traction_force = self.direction_vector * gas * self.engine_max_force
        drag = - self.drag_coef * self.vel * self.speed  # -C*v^2 but 2d vector
        friction = - self.friction_coef * self.vel
        self.acceleration = (traction_force + drag + friction) / self.mass

        # new speed
        new_rotation = math.degrees(math.atan2(self.direction_vector[0], -self.direction_vector[1])) - 90
        change_in_rotation = abs(new_rotation - self.rotation)
        if self.rotation > 90:      # vel has been reversed
            self.vel = 0
        else:
            self.vel += self.acceleration * delta_time
        # new position
        self.pos += self.vel * delta_time

        print(f"{time}: speed= {self.speed}, vel= {self.vel}")


        #self.rotation += turn * self.rotation_speed * delta_time
        #_x, _y = self.pos

        #_x += self.vel
        #self.pos = (_x, _y)

        """
        self.vel += gas * self.acceleration * delta_time
        if abs(self.vel) < 0.001:
            self.vel = 0
        else:
            self.vel -= self.friction * delta_time"""

    def draw(self, win):
        # self.pos = pygame.mouse.get_pos()

        # Rotate car
        self.rotated_img = pygame.transform.rotate(self.IMG, self.rotation)
        self.img_rect = self.rotated_img.get_rect(center=self.pos)

        win.blit(self.rotated_img, self.img_rect)


def draw_window(win, car):
    win.blit(RACE_TRACK_IMG, (0, 0))

    car.draw(win)

    pygame.display.update()


def main():
    # initiate pygame window
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    car = Car((100, 100))

    run = True
    while run:
        # 30 FPS
        delta_time = clock.tick(FPS)/1000

        # Check user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Close window
                run = False
                pygame.quit()
                quit()
        if keyboard.is_pressed("z"):
            gas = 1
        elif keyboard.is_pressed("s"):
            gas = -1
        else:
            gas = 0

        car.move(gas, 0, delta_time, pygame.time.get_ticks())

        # draw window
        draw_window(win, car)


main()
