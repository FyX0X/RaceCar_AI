import math
import time

import pygame
import numpy as np
import pickle
import os

TRACK_IMG_PATH = os.path.join("imgs", "race_track.png")
# green color = rgba(34,177,76,255)


class CheckPoint:

    def __init__(self, pos, radius, _id):
        self.pos = pos
        self.radius = radius
        self.id = _id

    def draw(self, win):
        pygame.draw.circle(win, (255, 255, 255, 127), self.pos, self.radius, 2)


class TrackFile:

    def __init__(self, checkpoints, bg_color, size, img_path):
        self.checkpoints = checkpoints
        self.bg_color = bg_color
        self.size = size
        self.img_path = img_path

    def save_track_file(self, file_path):
        with open(file_path, "wb") as file:
            pickle.dump(self, file)


class RaceTrack:
    NUMBER_OF_WINNING_LAP = 10

    def __init__(self, img_path, bg_color, size, cp_list=[]):
        self.checkpoints = cp_list
        self.start_pos = (367, 63)
        self.show_checkpoints = False

        self.size = size
        self.img_path = img_path
        self.img = pygame.image.load(img_path)
        self.bg_color = bg_color
        self.bg = pygame.Surface(size)
        self.bg.fill(bg_color)

    @staticmethod
    def load_from_track_file(file_path):
        with open(file_path, "rb") as file:
            track_file = pickle.load(file)
        track = RaceTrack(track_file.img_path, track_file.bg_color, track_file.size, track_file.checkpoints)
        track.start_pos = track_file.checkpoints[0].pos
        return track

    def save_track(self, file_path):
        track_file = TrackFile(self.checkpoints, self.bg_color, self.size, self.img_path)
        track_file.save_track_file("track.pickle")

    def load_checkpoints(self):
        pass

    def draw(self, win):
        win.blit(self.bg, (0, 0))
        win.blit(self.img, (0, 0))
        if self.show_checkpoints:
            for cp in self.checkpoints:
                cp.draw(win)

    def get_mask(self):
        _mask = pygame.mask.from_surface(self.img)
        _mask.invert()
        return _mask

    def collide(self, car):
        to_return = [False, 0]
        car_mask = car.get_mask()
        track_mask = self.get_mask()

        car_x, car_y = car.pos

        checking_cp = True
        while checking_cp:
            cp_nb = car.distance%len(self.checkpoints)
            next_cp = self.checkpoints[cp_nb]
            cp_x, cp_y = next_cp.pos
            dist_with_cp = math.sqrt((car_x - cp_x) ** 2 + (car_y - cp_y) ** 2)
            checking_cp = False
            if dist_with_cp <= next_cp.radius:
                car.distance += 1
                checking_cp = True          # continue to check next cp
                to_return[1] += 1        # only for neat algorithm
                if cp_nb == 0:
                    car.lap += 1
                    to_return[1] += 10
                    if car.lap > self.NUMBER_OF_WINNING_LAP:
                        car.won = True


        """
        for cp in self.checkpoints:
            cp_x, cp_y = cp.pos
            dist_with_cp = math.sqrt((car_x-cp_x)**2 + (car_y-cp_y)**2)
            if dist_with_cp <= cp.radius and cp.id + car.lap*len(self.checkpoints) - car.distance == 1:
                car.distance += 1
                if car.distance == len(self.checkpoints):
                    car.lap += 1
                if car.distance >= len(self.checkpoints)*self.NUMBER_OF_WINNING_LAP:

                    car.won = True"""

        x, y, w, h = car.get_rect()
        overlap_point = track_mask.overlap(car_mask, (x, y))

        # track_mask.draw(car_mask, (x, y))
        # mask_img = track_mask.to_surface()
        if overlap_point:
            to_return[0] = True
            return to_return
        return to_return


class TrackMaker:

    def __init__(self, path_to_image, _size, _start_pos=(0, 0), color=(34,177,76,255)):

        # img = pygame.image.load(path_to_image)
        self.track = RaceTrack(path_to_image, color, _size)
        self.track.show_checkpoints = True
        self.cp_number = 0

        self.pos1 = None
        self.pos2 = None

    def do_all_checkpoint(self, pos, radius, first=False):
        print("check pos for new CP")
        working_cp = True
        x, y = pos

        # place first CP
        if first:
            self.track.checkpoints.append(CheckPoint((x, y), radius, 0))

        _id = len(self.track.checkpoints)
        old_x, old_y = self.track.checkpoints[_id-1].pos
        print("last CP pos: ", old_x, old_y)
        print("mouse pos: ", x, y)


        # calculate distance with last CP
        dist = math.sqrt((x-old_x)**2 + (y-old_y)**2)
        if dist >= 5:
            self.track.checkpoints.append(CheckPoint((x, y), radius, _id))
            print("checkpoint placed")

    """
    def new_cp_click(self, pos):
        if self.pos1 is None:
            self.pos1 = pos
        elif self.pos2 is None:
            self.pos2 = pos
            self.new_checkpoint()
            self.pos1 = None
            self.pos2 = None"""

    """
    def new_checkpoint(self):
        x1, y1 = self.pos1
        x2, y2 = self.pos2
        center_pos = ((x1+x2)/2, (y1+y2)/2)
        diameter = math.sqrt((x2-x1)**2 + (y2-y1)**2)
        id = len(self.track.checkpoints)
        self.track.checkpoints.append(CheckPoint(center_pos, diameter/2, id))
        print("checkpoint placed")"""

    def finish(self, file_path):
        print("stop recording checkpoints")

        # creating "pickle-able" object
        track_file = TrackFile(self.track.checkpoints, self.track.bg_color, self.track.size, self.track.img_path)

        with open(file_path, "wb") as file:
            pickle.dump(track_file, file)
            print("track saved in: ", file_path)

    def draw(self, win):
        self.track.draw(win)


def draw_window(win, track_maker):
    track_maker.draw(win)

    pygame.display.update()


if __name__ == "__main__":

    pygame.init()

    max_time_delay_for_escape = 500
    escape_time = 0

    path_to_track = os.path.join("track.pickle")

    start_pos = (0, 0)
    size = (600, 600)
    win = pygame.display.set_mode(size)
    pygame.display.set_caption("Track Maker")

    #creating_cp = True
    already_started = False
    done = False
    current_cp_radius = 25

    track_maker = TrackMaker(TRACK_IMG_PATH, size, start_pos)
    print("track object initiated")
    print("begin placing checkpoints, press escape two times to escape")

    run = True
    while run:
        # do all cp if already started:
        if already_started and not done:
            track_maker.do_all_checkpoint(pygame.mouse.get_pos(), current_cp_radius)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p or already_started:
                    if not already_started:
                        track_maker.do_all_checkpoint(pygame.mouse.get_pos(), current_cp_radius, True)
                        already_started = True

                if event.key == pygame.K_UP:
                    current_cp_radius += 5
                if event.key == pygame.K_DOWN:
                    current_cp_radius -= 5

                if event.key == pygame.K_ESCAPE:
                    if pygame.time.get_ticks() - escape_time <= max_time_delay_for_escape:
                        done = True
                        track_maker.finish(path_to_track)
                    escape_time = pygame.time.get_ticks()
            """
            if creating_cp and event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                track_maker.new_cp_click(pos)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if pygame.time.get_ticks() - escape_time <= max_time_delay_for_escape:
                        creating_cp = False
                        track_maker.finish(path_to_track)
                    escape_time = pygame.time.get_ticks()"""

        draw_window(win, track_maker)