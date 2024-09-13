import math

import pygame
import numpy as np
import pickle
import os

TRACK_IMG_PATH = os.path.join("imgs", "race_track.png")
# green color = rgba(34,177,76,255)


class CheckPoint:

    def __init__(self, pos, radius, id):
        self.pos = pos
        self.radius = radius
        self.id = id

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

    def collide(self, car):
        car_mask = car.get_mask()
        track_mask = pygame.mask.from_surface(self.img)
        track_mask.invert()

        x, y, w, h = car.img_rect
        overlap_point = track_mask.overlap(car_mask, (x, y))

        #track_mask.draw(car_mask, (x, y))
        #mask_img = track_mask.to_surface()
        if overlap_point:
            return True
        return False


class TrackMaker:

    def __init__(self, path_to_image, size, start_pos=(0, 0), color=(34,177,76,255)):
        img = pygame.image.load(path_to_image)
        self.track = RaceTrack(img, start_pos, color, size)
        self.track.show_checkpoints = True
        self.cp_number = 0

        self.pos1 = None
        self.pos2 = None

    def new_cp_click(self, pos):
        if self.pos1 is None:
            self.pos1 = pos
        elif self.pos2 is None:
            self.pos2 = pos
            self.new_checkpoint()
            self.pos1 = None
            self.pos2 = None

    def new_checkpoint(self):
        x1, y1 = self.pos1
        x2, y2 = self.pos2
        center_pos = ((x1+x2)/2, (y1+y2)/2)
        diameter = math.sqrt((x2-x1)**2 + (y2-y1)**2)
        id = len(self.track.checkpoints)
        self.track.checkpoints.append(CheckPoint(center_pos, diameter/2, id))
        print("checkpoint placed")

    def finish(self, file_path):
        print("stop recording checkpoints")

        with open(file_path, "wb") as file:
            pickle.dump(self.track, file)
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


    creating_cp = True

    track_maker = TrackMaker(TRACK_IMG_PATH, size, start_pos)
    print("track object initiated")
    print("begin placing checkpoints, press escape two times to escape")

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
            if creating_cp and event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                track_maker.new_cp_click(pos)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if pygame.time.get_ticks() - escape_time <= max_time_delay_for_escape:
                        creating_cp = False
                        track_maker.finish(path_to_track)
                    escape_time = pygame.time.get_ticks()

        draw_window(win, track_maker)