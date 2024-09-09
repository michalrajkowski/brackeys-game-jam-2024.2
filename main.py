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

# This is the actual player while on the sea?
class PlayerSurfboard:
    # ma x, y, rotation, speed, points of collision?
    def __init__(self, x, y, rotation) -> None:
        self.x = x
        self.y = y
        self.rotation = rotation
        # When drawing the board tou have to move it back by 8 units?
        self.col_points_ofset = ((-8,0), (0,0), (8,0))
        self.sprite = (0,16, 16, 16)

        self.rotation_speed = 0
        self.rotation_veloity = 0

        self.speed = 0
        self.velocity = 0
        self.max_speed = 0
        pass

    def get_rotated_points(self):
        pass
        p1_relative = self.rotate_point(self.col_points_ofset[0], self.rotation)
        p2_relative = (0,0)
        p3_relative = self.rotate_point(self.col_points_ofset[2], self.rotation)
        print("\n")
        print(self.rotation)
        print(f"p1: {p1_relative}")
        print(f"p2: {p2_relative}")
        print(f"p3: {p3_relative}")
        return (p1_relative, p2_relative, p3_relative)


    def rotate_point(self, point, degrees):
        theta = np.deg2rad(-1*degrees)
        x, y = point
        x_new = x * np.cos(theta) - y * np.sin(theta)
        y_new = x * np.sin(theta) + y * np.cos(theta)
        return (x_new, y_new)
    

    # FROM PLAYER SHIP
    def add_rotation(self, degree):
        self.rotation += degree
        self.rotation = (self.rotation+360)%360 # to make sure it is always 0-360 

    def try_rotate(self, forward=1.0):
        rotation_speed = 0.5
        rotate_degree = int(rotation_speed*forward*(1/30)*360)
        self.add_rotation(rotate_degree)

    def set_angle(self, angle):
        self.rotation = angle



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
        self.player_ship : PlayerShip = PlayerShip(-50,0,0)
        self.sea : Sea = Sea()
        self.player_surf : PlayerSurfboard = PlayerSurfboard(0,0,0)

        self.rem_points = []
        self.wave_points = []

        pyxel.run(self.update, self.draw)

    def update(self):
        self.handle_player_input()
        self.update_sea()
        self.surf_physics()
        self.update_ship_angle_sea()
        pass

    def draw(self):
        pyxel.cls(0)
        self.draw_sea()
        self.draw_ship()
        self.draw_serfer()
        self.draw_rem_points()
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
            self.player_surf.try_rotate(1.0)
        if pyxel.btn(pyxel.KEY_D):
            # try rotate right
            self.player_ship.try_rotate(-1.0)
            self.player_surf.try_rotate(-1.0)
        if pyxel.btn(pyxel.KEY_W):
            # HEAVE HO!
            self.player_ship.add_speed(5.0*(1/30))
        if pyxel.btn(pyxel.KEY_S):
            # SLOW DOWN!!!
            self.player_ship.add_speed(-5.0*(1/30))
    
    def surf_physics(self):
        # Physics of surfer board
        # (My brain hurts so much...)

        # Check for key points contacts:
        p_relative = self.player_surf.get_rotated_points()
        p_semi_absolute = []
        p_absolute = [] # changed by sea offset?

        # Adjust each point relative to the player's position and store as tuples
        for p in p_relative:
            # Create a new tuple with updated x and y coordinates
            semi_absolute_point = (p[0] + self.player_surf.x, p[1] + self.player_surf.y)
            p_semi_absolute.append(semi_absolute_point)
        
        
        # Draw those points:
        self.rem_points = p_semi_absolute

        wave_points = []
        for p in p_semi_absolute:
            wave_p = (p[0], self.sea.wave_function(p[0]+self.sea.sea_offset))
            wave_points.append(wave_p)
        self.wave_points = wave_points

        # Check if all points above the sea
        all_above = True
        for index, p in enumerate(p_semi_absolute):
            # check if this point is below sea level
            if int(p[1]) > int(wave_points[index][1]):
                all_above = False
                break

        if all_above:
            # Fall down:
            self.player_surf.y += 1
            new_points = []
            for p in p_semi_absolute:
                new_p = (p[0], p[1] + 1)
                new_points.append(new_p)
            semi_absolute_point = new_points

        # Check if any point below the sea
        any_below = False
        for index, p in enumerate(p_semi_absolute):
            # check if this point is below sea level
            if int(p[1]) > int(wave_points[index][1]):
                any_below = True
                break
        if any_below:
            # Fall down:
            self.player_surf.y -= 1
            new_points = []
            for p in p_semi_absolute:
                new_p = (p[0], p[1] - 1)
                new_points.append(new_p)
            semi_absolute_point = new_points

        # Najpierw rozpatrz skrajne punkty deski:
        # Przedni:
        # jeżeli punkt spoczywa fali : rotacja w lewo
        # Tylni:
        # jeżeli punkt spoczywa na fali : rotacja w prawo 

        # jeżeli żaden z nich: rotacja zgodna z osią fali

        # jeżeli dwa = no rotation

        # jeżeli jakikolwiek punkt jest pod falą - podnieś się o piksel w dół

        # jeżeli brak kontaktu - opuść się o piksel w dół


        pass

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
        

    def draw_serfer(self):

        pyxel.blt(self.player_surf.x + DRAW_X_OFFSET - 8, # We calculate for the origin point be at (8,0) and not (0,0)
                  self.player_surf.y + DRAW_Y_OFFSET - 8,
                  0,
                  self.player_surf.sprite[0],
                  self.player_surf.sprite[1],
                  self.player_surf.sprite[2],
                  self.player_surf.sprite[3],
                  0, self.player_surf.rotation)
        
        # Draw serfer points:
        relative_points = self.player_surf.get_rotated_points()
        for p in relative_points:
            (x_rel,y_rel) = p
            pyxel.pset(x_rel + DRAW_X_OFFSET, y_rel + self.player_surf.x + DRAW_Y_OFFSET + self.player_surf.y, 11)

        pass

    def draw_rem_points(self):
        for p in self.rem_points:
            pyxel.pset(p[0] + DRAW_X_OFFSET, p[1] + DRAW_Y_OFFSET, 2)
        for p in self.wave_points:
            pyxel.pset(p[0] + DRAW_X_OFFSET, p[1] + DRAW_Y_OFFSET,8)

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