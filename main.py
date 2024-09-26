#import time
import pygame
import os
import numpy as np
import math
import keyboard
import car_class
import race_track
from race_track import TrackFile
from race_track import CheckPoint


pygame.init()

WIN_WIDTH, WIN_HEIGHT = 600, 600
MAX_FPS = 30

RACE_TRACK_IMG = pygame.image.load(os.path.join("imgs", "race_track.png"))
CAR_IMG = pygame.transform.scale_by(pygame.image.load(os.path.join("imgs", "red_car.png")), 0.8)

TEXT_FONT = pygame.font.SysFont("comicsan", 20)

    # green color = rgba(34,177,76,255)


def draw_window(win, car, track, fps, show_mask=False):
    track.draw(win)        # draw background

    car.draw(win)     # draw car

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
        car_mask = car.get_mask()
        track_mask = pygame.mask.from_surface(track.img)
        track_mask.invert()
        x, y, w, h = car.img_rect
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
    pygame.display.update()


# changement
def main():
    # initiate pygame window
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    #track = race_track.RaceTrack(os.path.join("imgs", "race_track.png"),(34, 177, 76),  (WIN_WIDTH, WIN_HEIGHT))
    track = race_track.RaceTrack.load_from_track_file(os.path.join("track_1.pickle"))
    car = car_class.Car(track.start_pos, CAR_IMG)

    for i in range(8):
        vector = np.around(car.get_direction_vector_from_rotation(i*45), 2)

        print(f"angle: {i*45} => vector: {vector}")

    run = True
    while run:
        # 30 FPS
        delta_time = clock.tick(MAX_FPS*10) / 1000

        # Check user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Close window
                run = False
                pygame.quit()
                quit()
        throttle = 0
        steering = 0
        show_mask = False
        track.show_checkpoints = False
        if keyboard.is_pressed("z") and not keyboard.is_pressed("s"):
            throttle = 1
        elif keyboard.is_pressed("s") and not keyboard.is_pressed("z"):
            throttle = -1
        if keyboard.is_pressed("q") and not keyboard.is_pressed("d"):
            steering = 1
        elif keyboard.is_pressed("d") and not keyboard.is_pressed("q"):
            steering = -1
        if car.is_dead and keyboard.is_pressed("enter"):
            car = car_class.Car(track.start_pos, CAR_IMG)
        if car.won and keyboard.is_pressed("enter"):
            car = car_class.Car(track.start_pos, CAR_IMG)

        if keyboard.is_pressed("m"):
            show_mask = True
        if keyboard.is_pressed("p"):
            track.show_checkpoints = True

        if not car.is_dead and not car.won:
            car.move(throttle, steering, delta_time, pygame.time.get_ticks())

        if track.collide(car):
            car.is_dead = True

        car.update_timer()
        # draw window
        draw_window(win, car, track, clock.get_fps(), show_mask)


main()
