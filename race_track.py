import pygame
import numpy as np


class CheckPoint:

    def __init__(self):
        pass


class RaceTrack:

    def __init__(self, img, start_pos, bg_color, size):
        self.img = img
        self.start_pos = start_pos
        #self.bg_color = bg_color
        self.bg = pygame.Surface(size)
        self.bg.fill(bg_color)
        self.checkpoints = []

    def draw(self, win):
        win.blit(self.bg, (0, 0))
        win.blit(self.img, (0, 0))

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


