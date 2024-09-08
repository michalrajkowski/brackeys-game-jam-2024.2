import pyxel
import math
import numpy as np

(SCREEN_W, SCREEN_H) = (160, 120)
DRAW_X_OFFSET = 60
DRAW_Y_OFFSET = 80

# TODO:
# ship art and ship rotation?

def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))

class Sea:
    def __init__(self):
        self.sea_offset = 0.0
        # Wave function
    
    def wave_function(self, x):
        return 2 * np.sin(0.4 * x) + 4 * np.sin(0.1 * x)

    # Derivative of the wave function (slope)
    def wave_slope(self, x):
        return 0.4 * np.cos(0.1 * x) + 0.8 * np.cos(0.4 * x)

    # Calculate the ship's angle based on the wave slope
    def ship_angle(self, x):
        slope = self.wave_slope(x)
        angle = np.arctan2(-1, slope)  # Angle in radians
        return np.degrees(angle)  # Convert to degrees

class PlayerShip:
    def __init__(self, x, y, rotation):
        self.x = x
        self.y = y
        self.rotation = rotation
        self.speed = 0.0
        self.max_speed = 30.0
        self.sprite = (0,0,32,16) # x, y, w, h
        self.ship_anchor_point = (16, 16)
        pass
    
    def add_rotation(self, degree):
        self.rotation += degree
        self.rotation = (self.rotation+360)%360 # to make sure it is always 0-360 

    def add_speed(self, value):
        self.speed += value
        self.speed = clamp(self.speed, 0, 30.0)

    def try_rotate(self, forward=1.0):
        rotation_speed = 0.5
        rotate_degree = int(rotation_speed*forward*(1/30)*360)
        self.add_rotation(rotate_degree)

    def set_angle(self, angle):
        self.rotation = angle


class App:
    def __init__(self):
        pyxel.init(SCREEN_W, SCREEN_H, title="Sea food delivery service")
        pyxel.load("asset.pyxres")
        pyxel.mouse(True)

        # Initialize game components
        self.player_ship : PlayerShip = PlayerShip(0,0,0)
        self.sea : Sea = Sea()

        pyxel.run(self.update, self.draw)

    def update(self):
        self.handle_player_input()
        self.update_sea()
        self.update_ship_angle_sea()
        pass

    def draw(self):
        pyxel.cls(0)
        self.draw_sea()
        self.draw_ship()
        self.draw_stats()

    def handle_player_input(self):
        # Rotate the ship (A/D)
        # Increase Speed with W
        # breaks with S
        # Fire cannon with F?

        # Handle A/D
        if pyxel.btn(pyxel.KEY_A):
            # try rotate left
            self.player_ship.try_rotate(1.0)
        if pyxel.btn(pyxel.KEY_D):
            # try rotate right
            self.player_ship.try_rotate(-1.0)
        if pyxel.btn(pyxel.KEY_W):
            # HEAVE HO!
            self.player_ship.add_speed(5.0*(1/30))
        if pyxel.btn(pyxel.KEY_S):
            # SLOW DOWN!!!
            self.player_ship.add_speed(-5.0*(1/30))
    
    def update_sea(self):
        # TODO update the value by player ship real x offset from starting point?
        self.sea.sea_offset += 5 * (1/30)

    def update_ship_angle_sea(self):
        self.player_ship.y = self.sea.wave_function(self.player_ship.x + self.sea.sea_offset)
        sea_angle = self.sea.ship_angle(self.player_ship.x + self.sea.sea_offset)
        sea_angle = (int(-1.0*sea_angle - 90)+360)%360
        print(sea_angle)
        self.player_ship.set_angle(sea_angle)

    def draw_stats(self):
        # Draw ship speed and rotation
        pyxel.rect(0,0,64,32,0)
        pyxel.rectb(0,0,64,32,7)
        pyxel.text(1,1,f"speed: {round(self.player_ship.speed, 1)}",7)
        pyxel.text(1, 8, f"angle: {self.player_ship.rotation}", 7)

    def draw_ship(self):
        # Draw the ship sprite
        # Make sure it is properly rotated?
        pyxel.blt(self.player_ship.x + DRAW_X_OFFSET- self.player_ship.ship_anchor_point[0], 
                  self.player_ship.y + DRAW_Y_OFFSET - self.player_ship.ship_anchor_point[1], 
                  0, 
                  self.player_ship.sprite[0], 
                  self.player_ship.sprite[1], 
                  self.player_ship.sprite[2], 
                  self.player_ship.sprite[3], 0, self.player_ship.rotation)
        
        pass

    def draw_sea(self):
        # For each point on the screen get wave function and draw its pixel
        for i in range(SCREEN_W):
            pixel_x = i - DRAW_X_OFFSET
            pixel_y = self.sea.wave_function(pixel_x+self.sea.sea_offset)
            # Draw pixel based on this coordinates
            pyxel.pset(pixel_x + DRAW_X_OFFSET, pixel_y + DRAW_Y_OFFSET, 6)

        # Draw line for sea 90
        line_y = self.sea.wave_function(30+self.sea.sea_offset-DRAW_X_OFFSET)
        # print(line_y)

        line_angle = (self.sea.ship_angle(30+self.sea.sea_offset-DRAW_X_OFFSET) +90)
        # pyxel.blt(30+DRAW_X_OFFSET, line_y + DRAW_Y_OFFSET, 0, 0, 16, 16, 16, 0, line_angle)

App()