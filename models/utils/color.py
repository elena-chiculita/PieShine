import math


class Gamut(object):
    """
    Model of the gamut.

    See Philips documentation for formulas, etc.
    """


    def __init__(self, name, red_x, red_y, green_x, green_y, blue_x, blue_y):
        self.name = name
        self.red_x = float(red_x)
        self.red_y = float(red_y)
        self.green_x = float(green_x)
        self.green_y = float(green_y)
        self.blue_x = float(blue_x)
        self.blue_y = float(blue_y)
        self.red_green_m = (self.green_y - self.red_y) / (self.green_x - self.red_x)
        self.red_green_b = (self.red_y * self.green_x - self.red_x * self.green_y) / (self.green_x - self.red_x)
        self.green_blue_m = (self.blue_y - self.green_y) / (self.blue_x - self.green_x)
        self.green_blue_b = (self.green_y * self.blue_x - self.green_x * self.blue_y) / (self.blue_x - self.green_x)
        self.blue_red_m = (self.red_y - self.blue_y) / (self.red_x - self.blue_x)
        self.blue_red_b = (self.blue_y * self.red_x - self.blue_x * self.red_y) / (self.red_x - self.blue_x)

    def __repr__(self):
        str_format = ('*** Gamut %s ***\n' +
                      'R (%.2f, %.2f)\n' +
                      'G (%.2f, %.2f)\n' +
                      'B (%.2f, %.2f)\n' +
                      'RG: y = %.2fx + %.2f\n' +
                      'GB: y = %.2fx + %.2f\n' +
                      'BR: y = %.2fx + %.2f')
        str_vars = (self.name,
                    self.red_x, self.red_y,
                    self.green_x, self.green_y,
                    self.blue_x, self.blue_y,
                    self.red_green_m, self.red_green_b,
                    self.green_blue_m, self.green_blue_b,
                    self.blue_red_m, self.blue_red_b)
        return str_format % str_vars

    @staticmethod
    def point_projection(x, y, m, b):
        return (float(x + (m * y) - (m * b)) / ((m * m) + 1),
                float(((m * m) * y) + (m * x) + b) / ((m * m) + 1))

    @staticmethod
    def line_distance(x, y, m, b):
        return abs((m * x) - y + b) * (math.sqrt(1 / ((m * m) + 1)))

    @staticmethod
    def line_side(x, y, m, b):
        return y - m * x - b

    def inside_gamut(self, x, y):
        if ((self.line_side(x, y, self.red_green_m, self.red_green_b) <= 0) and
                (self.line_side(x, y, self.green_blue_m, self.green_blue_b) <= 0) and
                (self.line_side(x, y, self.blue_red_m, self.blue_red_b) >= 0)):
            return True
        return False

    def gamut_aprox(self, x, y):
        red_green_dist = self.line_distance(x, y, self.red_green_m, self.red_green_b)
        green_blue_dist = self.line_distance(x, y, self.green_blue_m, self.green_blue_b)
        blue_red_dist = self.line_distance(x, y, self.blue_red_m, self.blue_red_b)
        min_dist, m, b, x1, y1, x2, y2 = (
            sorted([(red_green_dist,  self.red_green_m,  self.red_green_b,  self.red_x,   self.red_y,   self.green_x, self.green_y),
                    (green_blue_dist, self.green_blue_m, self.green_blue_b, self.green_x, self.green_y, self.blue_x,  self.blue_y),
                    (blue_red_dist,   self.blue_red_m,   self.blue_red_b,   self.blue_x,  self.blue_y,  self.red_x,   self.red_y)],
                   key=lambda x: x[0])[0])
        x_projection, y_projection = self.point_projection(x, y, m, b)
        ends = sorted([(x_projection, y_projection), (x1, y1), (x2, y2)], key=lambda x: x[0])
        return ends[1]

    def get_xy_and_bri_from_rgb(self, red, green, blue):
        red = float(red) / 255
        green = float(green) / 255
        blue = float(blue) / 255
        red = pow((red + 0.055) / (1.0 + 0.055), 2.4) if red > 0.04045 else (red / 12.92)
        green = pow((green + 0.055) / (1.0 + 0.055), 2.4) if green > 0.04045 else (green / 12.92)
        blue = pow((blue + 0.055) / (1.0 + 0.055), 2.4) if blue > 0.04045 else (blue / 12.92)
        X = red * 0.664511 + green * 0.154324 + blue * 0.162028
        Y = red * 0.283881 + green * 0.668433 + blue * 0.047685
        Z = red * 0.000088 + green * 0.072310 + blue * 0.986039
        if X + Y + Z:
            x = X / (X + Y + Z)
            y = Y / (X + Y + Z)
            bri = int(Y * 255)
        else:
            x = 0.3227
            y = 0.329
            bri = 1
        if not self.inside_gamut(x, y):
            x, y = self.gamut_aprox(x, y)
        return x, y, bri
