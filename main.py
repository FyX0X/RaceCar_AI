#import time
import pygame
import os
import numpy as np
import math
import keyboard
import car_class

pygame.init()

WIN_WIDTH, WIN_HEIGHT = 600, 600
MAX_FPS = 30

RACE_TRACK_IMG = pygame.image.load(os.path.join("imgs", "race_track.png"))
CAR_IMG = pygame.transform.scale_by(pygame.image.load(os.path.join("imgs", "red_car.png")), 0.8)

TEXT_FONT = pygame.font.SysFont("comicsan", 20)

class Old_Car:
    IMG = CAR_IMG

    def __init__(self, pos):
        self.pos = np.array([float(pos[0]), float(pos[1])])  # 2d vector
        self.vel = np.zeros(2)  # 2d vector
        self.speed = 0  # scalar speed
        #self.acceleration = np.zeros(2)  # 2d vector
        self.direction_vector = np.array([1, 0])
        self.rotation = 180  # scalar angle
        self.reverse = False
        self.stopped = True

        self.engine_max_force = 200  # change value later
        self.drag_coef = 0.005
        self.friction_coef = self.drag_coef * 30
        self.engin_braking = 0.5
        #self.friction_coef = 0.3  # change value later    friction is approx 30x drag
        self.mass = 0.5

        self.img_rect = None
        self.rotated_img = None

    def get_speed(self, velocity=None):
        if velocity is None:
            velocity = self.vel
        return math.sqrt(velocity[0] ** 2 + velocity[1] ** 2)  # scalar speed

    def get_direction_vector(self, velocity=None):
        if velocity is None:
            velocity = self.vel
        speed = self.get_speed(velocity)
        if self.speed != 0:
            return velocity / speed
        else:
            return self.direction_vector

    def get_rotation(self, direction_vector=None):         # rotation from direction vector (or velocity)
        if direction_vector is None:
            direction_vector = self.direction_vector

        if self.reverse:
            return math.degrees(math.atan2(direction_vector[0], -direction_vector[1])) + 90
        else:

            return math.degrees(math.atan2(direction_vector[0], -direction_vector[1])) - 90

    def update(self):
        self.speed = self.get_speed()
        self.direction_vector = self.get_direction_vector()
        self.rotation = self.get_rotation()

        if self.speed == 0:
            self.stopped = True
        else:
            self.stopped = False

        """    def forward(self, throttle: float = 0, delta_time: float = 1/FPS, tick=-1):
        if self.reverse:
            return self.breaking(throttle, delta_time, tick)
        else:
            return self.gas( throttle, delta_time, tick)

    def backward(self, throttle: float = 0, delta_time: float = 1/FPS, tick=-1):
        if self.reverse:
            return self.gas(throttle, delta_time, tick)
        else:
            return self.breaking(throttle, delta_time, tick)"""

    def get_acceleration(self, throttle: float = 0):

        # calculate acceleration
        traction_force = self.direction_vector * throttle * self.engine_max_force
        drag = - self.drag_coef * self.vel * self.speed     # -C*v^2 but 2d vector
        friction = - self.friction_coef * self.vel          # -C*v but 2d vector

        net_force = traction_force + drag + friction

        # engine braking
        if throttle == 0:
            net_force -= self.engin_braking * self.direction_vector

        acceleration = net_force/self.mass

        return acceleration

    """
    def breaking(self, throttle: float = 0, delta_time: float = 1/FPS, tick = -1):
        if self.stopped:
            self.reverse = True

        # calculate acceleration
        traction_force = -self.direction_vector * throttle * self.engine_max_force
        drag = - self.drag_coef * self.vel * self.speed  # -C*v^2 but 2d vector
        friction = - self.friction_coef * self.vel
        acceleration = (traction_force + drag + friction) / self.mass

        return acceleration"""

    def set_new_velocity_state(self, new_velocity, throttle):          # change name later

        if self.stopped:
            if throttle > 0:
                self.reverse = False
                self.stopped = False
                self.vel = new_velocity
            elif throttle < 0:
                self.reverse = True
                self.stopped = False
                self.vel = new_velocity
            self.vel = np.zeros(2)
        else:
            new_rotation = self.get_rotation(new_velocity)
            change_in_rotation = abs(new_rotation - self.rotation)
            if change_in_rotation > 90:      # vel has been reversed
                print("reversed -> stopped")
                self.vel = np.zeros(2)
                self.stopped = True
            else:
                self.vel = new_velocity


    def move(self, throttle: float = 0, turn: float = 0, delta_time: float = 1 / MAX_FPS, tick=-1):
        # update all variables
        self.update()

        # calculate acceleration
        acceleration = self.get_acceleration(throttle)

        # new velocity
        new_vel = self.vel + acceleration * delta_time
        self.set_new_velocity_state(new_vel, throttle)

        # new position
        self.pos += self.vel * delta_time

        self.update()

        print(f"{tick}: vel= {self.vel}, stopped= {self.stopped}, reverse= {self.reverse}")


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


def draw_window(win, car, fps):
    win.blit(RACE_TRACK_IMG, (0, 0))        # draw background

    car.draw(win)     # draw car

    fps_text = TEXT_FONT.render(f"FPS: {round(fps)}", 1, (255, 255, 255))
    win.blit(fps_text, (WIN_WIDTH - fps_text.get_width() - 10, 10))

    pygame.display.update()


def main():
    # initiate pygame window
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    car = car_class.Car((100, 100), CAR_IMG)

    for i in range(8):
        vector = np.around(car.get_direction_vector_from_rotation(i*45), 2)

        print(f"angle: {i*45} => vector: {vector}")

    run = True
    while run:
        # 30 FPS
        delta_time = clock.tick(MAX_FPS) / 1000

        # Check user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Close window
                run = False
                pygame.quit()
                quit()
        throttle = 0
        steering = 0
        if keyboard.is_pressed("z") and not keyboard.is_pressed("s"):
            throttle = 1
        elif keyboard.is_pressed("s") and not keyboard.is_pressed("z"):
            throttle = -1
        if keyboard.is_pressed("q") and not keyboard.is_pressed("d"):
            steering = 1
        elif keyboard.is_pressed("d") and not keyboard.is_pressed("q"):
            steering = -1

        car.move(throttle, steering, delta_time, pygame.time.get_ticks())

        # draw window
        draw_window(win, car, clock.get_fps())


main()
