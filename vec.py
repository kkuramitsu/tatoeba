
# クラス定義
# ２年生向け
#
# 課題　https://colab.research.google.com/drive/13An5bAh5Kg1TEg7jUoP0pHtoYdcXmidv?usp=sharing
# !git clone https://github.com/kkuramitsu/tatoeba.git
# import tatoeba.vec from Vec

import math


class Vec(object):
    x: float
    y: float

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f'({self.x}, {self.y})'

    def length(self):
        return math.sqrt(self.x**2 + self.y**2)

    def __add__(self, v):
        return Vec(self.x + v.x, self.y+v.y)

    def __sub__(self, v):
        return Vec(self.x - v.x, self.y-v.y)

    def __mul__(self, v):
        return Vec(self.x * v, self.y * v)

    def __truediv__(self, v):
        return Vec(self.x / v, self.y / v)

    def inverse(self):
        return Vec(-self.x, -self.y)

    def normalize(self):
        d = self.length()
        return Vec(self.x/d, self.y/d)

    def dot(self, v):
        return self.x * v.x + self.y * v.y

    def cross(self, v):
        return self.x * v.y - self.y * v.x

    def isVertical(self, v):
        return abs(self.dot(v)) < 0.000001  # ほぼ0

    def isParallel(self, v):
        return abs(self.cross(v)) < 0.000001  # ほぼ0

    def rad(self, v):
        return math.acos(self.dot(v) / (self.length() * v.length()))

    def rotate(self, theta):
        return Vec(math.cos(theta)*self.x-math.sin(theta)*self.y, math.sin(theta)*self.x+math.cos(theta)*self.y)

    def transform(self, cx=150, cy=150, scale=100):
        return (int(cx + self.x*scale), int(cy - self.y*scale))
