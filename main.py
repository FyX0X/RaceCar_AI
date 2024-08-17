import pygame
import os

WIN_WIDTH, WIN_HEIGHT = 600, 600

RACE_TRACK_IMG = pygame.image.load(os.path.join("imgs", "race_track.png"))
CAR_IMG = pygame.transform.scale_by(pygame.image.load(os.path.join("imgs", "red_car.svg")), 0.2)


class Car:
    IMG = CAR_IMG

    def __init__(self, pos):
        self.pos = pos
        self.rotation = 90
        self.img_rect = None
        self.rotated_img = None

    def draw(self, win):
        self.rotation += 1  #test

        # Rotate car
        self.rotated_img = pygame.transform.rotate(self.IMG, self.rotation)
        self.img_rect = self.rotated_img.get_rect(center=self.pos)

        win.blit(self.rotated_img, self.pos)


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
        clock.tick(30)

        # Check user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Close window
                run = False
                pygame.quit()
                quit()

        # draw window
        draw_window(win, car)


main()
