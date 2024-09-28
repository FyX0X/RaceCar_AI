import pygame
import numpy as np
import math

# New python file, for new car physics


class DetectingRay:

    def __init__(self, delta_angle, length, track_mask):
        self.delta_angle = delta_angle
        self.length = length

        self.car_pos = None
        self.angle = None
        # self.start_pos = (0, 0)
        self.end_pos = None

        # creates a surface, centered on car, to draw line on it
        self.line_surface = pygame.Surface((2*length, 2*length))
        self.line_surface = self.line_surface.convert_alpha()
        self.line_surface.fill((0, 0, 0, 0))

        self.track_mask = track_mask

        self.measured_distance = 0
        self.collision_pos = (0, 0)

    def get_surface_coordinate(self, pos):
        x, y = pos
        _x = self.length + x
        _y = self.length - y
        _pos = (_x, _y)
        return _pos

    def update(self, car_pos, car_angle):
        # update variables
        self.car_pos = car_pos
        self.angle = math.radians(car_angle) + self.delta_angle

        # detects wall
        self.detect_wall()

        # calculate coord of line
        x_end = math.cos(self.angle) * self.length
        y_end = math.sin(self.angle) * self.length
        self.end_pos = (x_end, y_end)

        # clear line
        self.line_surface.fill((0, 0, 0, 0))
        # draw line on surface
        pygame.draw.line(self.line_surface, (255, 255, 255),
                         self.get_surface_coordinate((0, 0)),
                         self.get_surface_coordinate(self.end_pos), 1)
        # draw ree line for collision distance
        pygame.draw.line(self.line_surface, (255, 0, 0),
                         self.get_surface_coordinate((0, 0)),
                         self.get_surface_coordinate(self.collision_pos), 2)

    def detect_wall(self):

        step_x = math.cos(self.angle)
        step_y = - math.sin(self.angle)     # minus sign comes from pygame origin in top left and not bottom left


        # resets vision
        self.measured_distance = 1
        self.collision_pos = (step_x * self.length, -step_y * self.length)

        #check for actual collision
        for i in range(self.length):
            car_x, car_y = self.car_pos
            x, y = step_x * i, step_y * i
            result = self.track_mask.get_at((x + car_x, y + car_y))

            if result:
                self.measured_distance = i/self.length
                self.collision_pos = (x, -y)
                break
                # make sure break happens BEFORE line is out of screen, or else game crashes
                # entire track NEEDS to be surrounded by a bit of grass on all sides

    def draw(self, win):
        rect = self.line_surface.get_rect(center=self.car_pos)
        win.blit(self.line_surface, rect)


class Car:

    def __init__(self, pos, img, track_mask):
        self.pos = pos
        self.vel = np.zeros(2)
        self.acceleration = np.zeros(2)
        self.speed = 0
        self.reverse = False
        self.direction_vector = np.array([-1, 0])
        self.rotation = self.get_rotation()
        self.angular_velocity = 0

        self.engine_max_force = 200  # change value later
        self.drag_coefficient = 0.005
        self.friction_coefficient = self.drag_coefficient * 30
        self.engine_braking = 0.5
        self.mass = 0.5
        self.length = 0.5

        self.img = img
        self.rotated_img = pygame.transform.rotate(self.img, self.rotation)
        self.img_rect = self.rotated_img.get_rect(center=self.pos)          # set coordinate origin in center

        self.throttle = 0       # accelerating from -1 to 1
        self.steering_angle = 0       # turning from -40 to 40

        self.delta_time = 0

        self.is_dead = False

        self.distance = 0
        self.lap = 0
        self.timer = 0
        self.born_time = pygame.time.get_ticks()
        self.won = False

        self.rays = []
        self.ray_init(track_mask)
        self.show_rays = False

    def ray_init(self, track_mask, nb_rays=5):

        for i in range(nb_rays):
            delta_angle = -math.pi/2 + i*math.pi/(nb_rays-1)
            ray = DetectingRay(delta_angle, 250, track_mask)
            self.rays.append(ray)

    def update_car(self):
        self.update_timer()
        for ray in self.rays:
            ray.update(self.pos, self.rotation)

    def update_timer(self):
        if not self.won and not self.is_dead:
            self.timer = pygame.time.get_ticks() - self.born_time

    def draw(self, win):
        # Rotate car
        self.rotated_img = pygame.transform.rotate(self.img, self.rotation)
        self.img_rect = self.rotated_img.get_rect(center=self.pos)          # set coordinate origin in center

        win.blit(self.rotated_img, self.img_rect)     # draw car

        if self.show_rays:
            for ray in self.rays:
                ray.draw(win)

    def get_mask(self):
        return pygame.mask.from_surface(self.rotated_img)

    def move(self, throttle, steering, delta_time, tick):
        self.throttle = abs(throttle)
        max_steering_angle = self.get_max_steering_angle()                 # max angle decreases with speed
        self.steering_angle = math.radians(steering * max_steering_angle)   # max angle = (1 * 60)° if speed is low
        # print(max_steering_angle)
        self.delta_time = delta_time

        # calculate rotation before moving car
        if steering != 0:
            radius = self.get_curve_radius()
            self.angular_velocity = self.get_angular_vel(radius)

            # change orientation:
            if self.reverse:
                self.rotation -= self.angular_velocity * delta_time
            else:
                self.rotation += self.angular_velocity * delta_time
            # update direction vector
            self.direction_vector = self.get_direction_vector_from_rotation()
            if self.reverse:
                self.direction_vector *= -1
            self.vel = self.direction_vector * self.speed

        # calculate acceleration (velocity and position calculated automatically in the functions)
        if self.speed != 0:
            if not self.reverse:
                if throttle > 0:
                    self.accelerating()
                elif throttle <= 0:
                    self.braking()
            else:
                if throttle < 0:
                    self.accelerating()
                elif throttle >= 0:
                    self.braking()
        else:
            if throttle > 0:
                self.accelerating()
            elif throttle < 0:
                print(f"{tick}: flip")
                self.reverse = True
                self.direction_vector *= -1
                self.accelerating()         # change with new, backward()

        self.update_physics()
        print(f"{tick}: vel= {self.vel}, dir_v= {self.direction_vector}, angle: {self.rotation}, reverse= {self.reverse}")

        """
        # calculate velocity
        self.update_vel()
        # calculate position
        self.update_pos()
        """

    def get_max_steering_angle(self, speed=None):
        if speed is None:
            speed = self.speed
        return max(80 - 4 * math.sqrt(self.speed), 20)  # max angle decreases with speed

    def get_angular_vel(self, curve_radius, speed=None):
        if speed is None:
            speed = self.get_speed()
        if curve_radius is None:
            return 0
        else:
            return speed/curve_radius

    def get_curve_radius(self, steering_angle=None):
        if steering_angle is None:
            steering_angle = self.steering_angle
        if steering_angle != 0:
            return self.length / math.sin(steering_angle)
        else:
            return None

    def get_direction_vector_from_rotation(self, rotation=None):
        if rotation is None:
            rad_rotation = math.radians(self.rotation)
        else:
            rad_rotation = math.radians(rotation)
        direction_vector = np.zeros(2)
        direction_vector[0] = math.cos(rad_rotation)
        direction_vector[1] = -math.sin(rad_rotation)

        return direction_vector

    def update_physics(self):
        self.speed = self.get_speed()
        self.direction_vector = self.get_direction_vector()
        self.rotation = self.get_rotation()

    def get_direction_vector(self, velocity=None):
        if velocity is None:
            velocity = self.vel
        speed = self.get_speed(velocity)
        if speed != 0:
            return velocity / speed
        else:
            return self.direction_vector

    def get_rotation(self, direction_vector=None, reverse=None):      # rotation from direction vector
        if direction_vector is None:
            direction_vector = self.get_direction_vector()
        if reverse is None:
            reverse = self.reverse
        if reverse:
            angle = math.degrees(math.atan2(direction_vector[0], direction_vector[1])) + 90
        else:
            angle = math.degrees(math.atan2(direction_vector[0], direction_vector[1])) - 90
        # print(f"dir_v: {direction_vector}, angle: {angle}       (with reverse = {reverse})")
        return angle

    def get_speed(self, velocity=None):
        if velocity is None:
            velocity = self.vel
        return math.sqrt(velocity[0] ** 2 + velocity[1] ** 2)  # scalar speed

    def accelerating(self):
        print("accelerating")
        traction_force = self.engine_max_force * self.throttle * self.direction_vector
        friction_force = -self.friction_coefficient * self.vel
        drag_force = -self.drag_coefficient * self.vel * self.speed

        net_force = traction_force + friction_force + drag_force
        self.acceleration = net_force / self.mass

        # update vel
        self.vel += self.acceleration * self.delta_time

        # update pos
        self.pos += self.vel * self.delta_time

        # self.update_vel(acceleration)

    def braking(self):
        print("braking")
        braking_force = - self.engine_max_force * self.throttle * self.direction_vector   # -throttle < 0
        friction_force = -self.friction_coefficient * self.vel
        drag_force = -self.drag_coefficient * self.vel * self.speed
        engine_braking_force = - self.engine_braking * self.direction_vector

        net_force = braking_force + friction_force + drag_force + engine_braking_force
        self.acceleration = net_force / self.mass

        # check if going to flip direction and updates vel
        new_vel = self.vel + self.acceleration * self.delta_time
        new_direction = self.get_direction_vector(new_vel)

        if np.isclose(new_direction, -self.direction_vector).all():     # direction has been reversed
            self.stop()
        else:                                               # direction has not been reversed
            self.vel = new_vel

        # update pos
        self.pos += self.vel * self.delta_time

        # return acceleration

    def update_vel(self):

        self.vel += self.acceleration * self.delta_time

    def update_pos(self):
        self.pos += self.vel * self.delta_time

    def stop(self):
        print("stop")
        self.vel = np.zeros(2)              # set velocity to 0
        if self.reverse:                    # if reversed:
            print("reverse => flip")
            self.direction_vector *= -1      # -> flips direction vector
        self.reverse = False                # set reverse to false
