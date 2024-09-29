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
import NNetworkDisplay

import neat

PATH_TO_OPEN = "GENOMES/Racer_time_cap_p150_gen_80.pickle"


pygame.init()

WIN_WIDTH, WIN_HEIGHT = 600, 600
MAX_FPS = 60

RACE_TRACK_IMG = pygame.image.load(os.path.join("imgs", "race_track.png"))
CAR_IMG = pygame.transform.scale_by(pygame.image.load(os.path.join("imgs", "red_car.png")), 0.8)

TEXT_FONT = pygame.font.SysFont("comicsan", 20)

    # green color = rgba(34,177,76,255)


def draw_window(win, car, track, fps, show_mask=False, show_rays=False, genome=None):
    track.draw(win)        # draw background

    # car.draw(win)     # draw car
    # draw all car in list
    car.draw(win, show_rays)

    fps_text = TEXT_FONT.render(f"FPS: {round(fps)}", 1, (255, 255, 255))
    win.blit(fps_text, (WIN_WIDTH - fps_text.get_width() - 10, 10))

    mouse_pos_text = TEXT_FONT.render(f"mouse pos: {pygame.mouse.get_pos()}", 1, (255, 255, 255))
    win.blit(mouse_pos_text, (WIN_WIDTH - mouse_pos_text.get_width() - 10, WIN_HEIGHT - mouse_pos_text.get_height() - 10))

    distance_text = TEXT_FONT.render(f"Distance: {car.distance}", 1, (255, 255, 255))
    win.blit(distance_text, (10, 10))
    timer_text = TEXT_FONT.render(f"Time: {round(car.timer/1000, 2)}", 1, (255, 255, 255))
    win.blit(timer_text, (10, 25))
    lap_text = TEXT_FONT.render(f"Lap: {car.lap}", 1, (255, 255, 255))
    win.blit(lap_text, (10, 40))

    if show_mask:
        track_mask = pygame.mask.from_surface(track.img)
        track_mask.invert()
        car_mask = car.get_mask()
        x, y, w, h = car.get_rect()
        track_mask.draw(car_mask, (x, y))
        mask_img = track_mask.to_surface()
        win.blit(mask_img, (0, 0))

    if car.is_dead:
        die_text = TEXT_FONT.render("You died", 1, (255, 255, 255))
        win.blit(die_text, (WIN_WIDTH / 2 - die_text.get_width() / 2, WIN_HEIGHT / 2 - die_text.get_height()))

        die_text = TEXT_FONT.render("Press enter to play again", 1, (255, 255, 255))
        win.blit(die_text, (WIN_WIDTH / 2 - die_text.get_width() / 2, WIN_HEIGHT / 2))

        game_over_screen = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
        game_over_screen.fill((0, 0, 0))
        game_over_screen.set_alpha(160)
        win.blit(game_over_screen, (0, 0))

    if car.won:
        won_text = TEXT_FONT.render("You won", 1, (255, 255, 255))
        win.blit(won_text, (WIN_WIDTH / 2 - won_text.get_width() / 2, WIN_HEIGHT / 2 - won_text.get_height()))

        won_text = TEXT_FONT.render("Press enter to play again", 1, (255, 255, 255))
        win.blit(won_text, (WIN_WIDTH / 2 - won_text.get_width() / 2, WIN_HEIGHT / 2))

        won_screen = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
        won_screen.fill((0, 0, 0))
        won_screen.set_alpha(160)
        win.blit(won_screen, (0, 0))


    # DRAW Neural Network
    white_bg = pygame.Surface((WIN_WIDTH//2, WIN_HEIGHT))
    white_bg.fill((255, 255, 255))
    win.blit(white_bg, (WIN_WIDTH, 0))

    # NN TITLE
    NNdisplay_text = TEXT_FONT.render("Neural Network: ", 1, (0, 0, 0))
    win.blit(NNdisplay_text, (WIN_WIDTH + 10, 10))

    # SCHEMA
    net_size = (WIN_WIDTH//2 - 20, WIN_HEIGHT - 20 - NNdisplay_text.get_height())
    net_pos = (WIN_WIDTH + 10, 10 + NNdisplay_text.get_height())

    layers, weighted_connections = NNetworkDisplay.load_network(config, genome)

    NNetworkDisplay.draw_network(win, layers, weighted_connections, net_size, net_pos)

    pygame.display.update()


# changement
def main(genome, config):

    # initiate pygame window
    win = pygame.display.set_mode((int(WIN_WIDTH * 1.5), WIN_HEIGHT))
    clock = pygame.time.Clock()

    net = neat.nn.FeedForwardNetwork.create(genome, config)
    # track = race_track.RaceTrack(os.path.join("imgs", "race_track.png"),(34, 177, 76),  (WIN_WIDTH, WIN_HEIGHT))
    track = race_track.RaceTrack.load_from_track_file(os.path.join("track_1.pickle"))
    car = car_class.Car(track.start_pos, CAR_IMG, track.get_mask())

    run = True
    while run:

        # 60 FPS
        delta_time = clock.tick(10) / 1000

        # delta_time = min(delta_time, 0.1)    # arbitrary, to not make physics engine crash => dt is in [0.05;0.1]
        # delta_time = max(0.05, delta_time)


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
        if car.is_dead and keyboard.is_pressed("enter"):
            car = car_class.Car(track.start_pos, CAR_IMG, track.get_mask())
        if car.won and keyboard.is_pressed("enter"):
            car = car_class.Car(track.start_pos, CAR_IMG, track.get_mask())

        # calculate car action
        if not car.is_dead and not car.won:
            input_list = []
            for ray in car.rays:
                input_list.append(ray.measured_distance)
            output = net.activate(input_list)            # output of type [throttle, steering]
            throttle, steering = output
            car.move(throttle, steering, delta_time, pygame.time.get_ticks())

        # check for wall collision
        if track.collide(car)[0]:       # track.collide() return list => [collision: bool, fitness: float]
            car.is_dead = True

        car.update_car()

        # draw window
        draw_window(win, car, track, clock.get_fps(), show_mask, show_rays, genome)






if __name__ == "__main__":

    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config_neat.txt")

    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_path)

    with open(PATH_TO_OPEN, "rb") as file:
        ai_controller = pickle.load(file)

    main(ai_controller, config)
