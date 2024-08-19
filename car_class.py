import pygame
import numpy as np
import math

# New python file, for new car physics


class Car:

    def __init__(self, pos, img):
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
        self.img_rect = None
        self.rotated_img = None

        self.throttle = 0       # accelerating from -1 to 1
        self.steering_angle = 0       # turning from -40 to 40

        self.delta_time = 0

    def draw(self, win):
        # Rotate car
        self.rotated_img = pygame.transform.rotate(self.img, self.rotation)
        self.img_rect = self.rotated_img.get_rect(center=self.pos)          # set coordinate origin in center

        win.blit(self.rotated_img, self.img_rect)     # draw car

    def move(self, throttle, steering, delta_time, tick):
        self.throttle = abs(throttle)
        max_steering_angle = self.get_max_steering_angle()                 # max angle decreases with speed
        self.steering_angle = math.radians(steering * max_steering_angle)   # max angle = (1 * 60)° if speed is low
        print(max_steering_angle)
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

        self.update()
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

    def update(self):
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
