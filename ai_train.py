#import time
import pygame
import os
import numpy as np
import math
import keyboard
import car_class
import race_track
import pickle
from race_track import TrackFile
from race_track import CheckPoint

import neat
import multiprocessing


pygame.init()

WIN_WIDTH, WIN_HEIGHT = 600, 600
MAX_FPS = 60

RACE_TRACK_IMG = pygame.image.load(os.path.join("imgs", "race_track.png"))
CAR_IMG = pygame.transform.scale_by(pygame.image.load(os.path.join("imgs", "red_car.png")), 0.8)

TEXT_FONT = pygame.font.SysFont("comicsan", 20)

    # green color = rgba(34,177,76,255)

# AI STUFF
gen = -1
TIME_PENALTY = 2
DISTANCE_BONUS_COEFFICIANT = 10
DEATH_PENALTY = 5

# OPTION
MAX_GEN = 400
SHOW_GRAPHICS = False
START_ITERATION = 100
ITERATION_FACTOR = 10

LABEL = "tc_60_p150"


def draw_window(win, cars_list, track, fps, show_mask=False, show_rays=False):
    track.draw(win)        # draw background

    # car.draw(win)     # draw car
    # draw all car in list
    for car in cars_list:
        car.draw(win, show_rays)

    fps_text = TEXT_FONT.render(f"FPS: {round(fps)}", 1, (255, 255, 255))
    win.blit(fps_text, (WIN_WIDTH - fps_text.get_width() - 10, 10))

    mouse_pos_text = TEXT_FONT.render(f"mouse pos: {pygame.mouse.get_pos()}", 1, (255, 255, 255))
    win.blit(mouse_pos_text, (WIN_WIDTH - mouse_pos_text.get_width() - 10, WIN_HEIGHT - mouse_pos_text.get_height() - 10))

    if len(cars_list) > 0:
        best_dist = 0
        for car in cars_list:
            if car.distance > best_dist:
                best_dist = car.distance
                best_car = car
        distance_text = TEXT_FONT.render(f"Distance: {best_dist}", 1, (255, 255, 255))
        win.blit(distance_text, (10, 10))
        timer_text = TEXT_FONT.render(f"Time: {round(best_car.timer/1000, 2)}", 1, (255, 255, 255))
        win.blit(timer_text, (10, 25))
        lap_text = TEXT_FONT.render(f"Lap: {best_car.lap}", 1, (255, 255, 255))
        win.blit(lap_text, (10, 40))

    if show_mask:
        track_mask = pygame.mask.from_surface(track.img)
        track_mask.invert()
        for car in cars_list:
            car_mask = car.get_mask()
            x, y, w, h = car.img_rect
            track_mask.draw(car_mask, (x, y))
        mask_img = track_mask.to_surface()
        win.blit(mask_img, (0, 0))

    """
    if car.is_dead:
        die_text = TEXT_FONT.render("You died", 1, (255, 255, 255))
        win.blit(die_text, (WIN_WIDTH / 2 - die_text.get_width() / 2, WIN_HEIGHT / 2 - die_text.get_height()))

        die_text = TEXT_FONT.render("Press enter to play again", 1, (255, 255, 255))
        win.blit(die_text, (WIN_WIDTH / 2 - die_text.get_width() / 2, WIN_HEIGHT / 2))

        game_over_screen = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
        game_over_screen.fill((0, 0, 0))
        game_over_screen.set_alpha(160)
        win.blit(game_over_screen, (0, 0))"""
    """
    if car.won:
        won_text = TEXT_FONT.render("You won", 1, (255, 255, 255))
        win.blit(won_text, (WIN_WIDTH / 2 - won_text.get_width() / 2, WIN_HEIGHT / 2 - won_text.get_height()))

        won_text = TEXT_FONT.render("Press enter to play again", 1, (255, 255, 255))
        win.blit(won_text, (WIN_WIDTH / 2 - won_text.get_width() / 2, WIN_HEIGHT / 2))

        won_screen = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
        won_screen.fill((0, 0, 0))
        won_screen.set_alpha(160)
        win.blit(won_screen, (0, 0))"""

    pygame.display.update()


# changement
def main(genomes, config):          # same as: def eval_genomes():
    global gen
    gen += 1

    nets = []
    ge = []
    cars = []

    physics_iteration = 0


    # initiate pygame window
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    # track = race_track.RaceTrack(os.path.join("imgs", "race_track.png"),(34, 177, 76),  (WIN_WIDTH, WIN_HEIGHT))
    track = race_track.RaceTrack.load_from_track_file(os.path.join("track_1.pickle"))

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        cars.append(car_class.Car(track.start_pos, CAR_IMG, track.get_mask()))
        g.fitness = 0
        ge.append(g)

    run = True
    while run:

        if len(cars) == 0:
            run = False
            break


        # 60 FPS
        delta_time = clock.tick(MAX_FPS*10) / 1000

        # delta_time = min(delta_time, 0.1)    # arbitrary, to not make physics engine crash => dt is in [0.05;0.1]
        # delta_time = max(0.05, delta_time)

        delta_time = 0.0166
        physics_iteration += 1

        # Check user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Close window
                run = False
                pygame.quit()
                quit()


        show_mask = False
        show_rays = False
        track.show_checkpoints = False
        save = False

        best_genome = None
        best_car = None

        # visual only
        if keyboard.is_pressed("m"):
            show_mask = True
        if keyboard.is_pressed("p"):
            track.show_checkpoints = True
        if keyboard.is_pressed("o"):
            show_rays = True
        if keyboard.is_pressed("i"):
            save = True

        cars_to_delete = []

        best_distance = 0
        for x, car in enumerate(cars):

            # find current best_car
            if car.distance > best_distance:
                best_genome = ge[x]
                best_car = car
                best_distance = car.distance


            # ge[x].fitness -= TIME_PENALTY       # penalty for being slow

            # calculate car action
            input_list = []
            for ray in car.rays:
                input_list.append(ray.measured_distance)
            output = nets[x].activate(input_list)            # output of type [throttle, steering]
            throttle, steering = output
            car.move(throttle, steering, delta_time, pygame.time.get_ticks())
            # ge[x].fitness += track.collide(car)[1] * DISTANCE_BONUS_COEFFICIANT

            # check for wall collision
            if track.collide(car)[0]:       # track.collide() return list => [collision: bool, fitness: float]
                car.is_dead = True
                cars_to_delete.append(car)
                # ge[x].fitness -= DEATH_PENALTY         # penalty for dying

            # remove slow cars to improve perf
            if car.distance < best_distance/3 - 10:
                cars_to_delete.append(car)

            car.update_car()

        """
        if not car.is_dead and not car.won:
            car.move(throttle, steering, delta_time, pygame.time.get_ticks())"""

        # END AFTER CERTAIN DELAY
        if len(cars) > 0:       # max time increases with gen (mx+p) ; caps out after certain number of gen (50)
            if physics_iteration >= min(START_ITERATION + ITERATION_FACTOR * gen, START_ITERATION + ITERATION_FACTOR*70):
                for x, car in enumerate(cars):
                    cars_to_delete.append(car)

        # remove cars to delete
        for dead_car in cars_to_delete:
            for car in cars:
                if dead_car == car:
                    x = cars.index(car)
                    ge[x].fitness = car.distance
                    cars.pop(x)
                    nets.pop(x)
                    ge.pop(x)

        # saves genome manually
        if save and best_genome is not None:
            print("SAVING a genome")
            with open(f"GENOMES/_Racer_{LABEL}_gen{gen}.pickle", "wb") as file:
                pickle.dump(best_genome, file)
        # automatic save
        if best_car is not None and gen % 10 == 0:                  # saves every ten gen
            with open(f"GENOMES/Racer_{LABEL}_gen_{gen}.pickle", "wb") as file:
                pickle.dump(best_genome, file)

        # draw window
        if SHOW_GRAPHICS:
            draw_window(win, cars, track, clock.get_fps(), show_mask, show_rays)


def run(_config):

    pop = neat.Population(_config)

    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)

    winner = pop.run(main, MAX_GEN)

    with open(f"GENOMES/Winner_{LABEL}", "wb") as file:
        pickle.dump(winner, file)


if __name__ == "__main__":

    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config_neat.txt")

    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_path)

    run(config)
