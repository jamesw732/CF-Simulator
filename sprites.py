import pygame as pg
from settings import *
from A_Star import *
import math
import random

class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((tilesize, tilesize))
        self.image.fill(player_color)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y

    def movegoal(self, goal):
        mousex = math.floor(goal[0]/tilesize)
        mousey = math.floor(goal[1]/tilesize)
        goal = (mousex, mousey)
        return goal

    def pathfind(self, graph, start, goal):
        came_from, cost_so_far = a_star_search(graph, start, goal)  # (self.x, self.y), (self.movegoal((pg.mouse.get_pos()[0], pg.mouse.get_pos()[1])))
        path = reconstruct_path(came_from, start, goal)
        return path

    def update(self):
        self.rect.x = self.x * tilesize
        self.rect.y = self.y * tilesize


class Ferret(pg.sprite.Sprite):
    def __init__(self, game, x, y, color, pad):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((tilesize, tilesize))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.color = color
        self.pad = pad
        self.path = []
        self.neighbors = []
        self.smallneighbors = []
        self.checkx = False
        self.checky = False
        self.afraid = False
        self.thbbt = False

    def on_pad(self):
        return (self.x, self.y) == (self.pad.x, self.pad.y)

    def get_small_neighbors(self):
        self.smallneighbors = []
        for i in [(self.x+1, self.y), (self.x-1, self.y), (self.x, self.y+1), (self.x, self.y-1)]:
            if i not in Wall.wallList and i[0] >= 0 and i[0] <= 13 and 0 <= i[1] and i[1] <= 13:
                self.smallneighbors.append(i)

    def scare(self):
        if (self.x, self.y) != (self.pad.x, self.pad.y):
            self.get_small_neighbors()
            choices = self.smallneighbors
            for i in [(self.x+1, self.y-1),(self.x+1, self.y-1), (self.x-1, self.y+1), (self.x-1, self.y-1)]:
                if i[0] >= 0 and i[0] <= 13 and 0 <= i[1] and i[1] <= 13 and i not in Wall.wallList:
                    choices.append(i)
            (self.x, self.y) = random.choice(choices)
            self.afraid = False

    def neighborfind(self):
        self.neighbors = []
        for a in [-2, -1, 0, 1, 2]:
            for b in [-2, -1, 0, 1, 2]:
                self.neighbors.append((self.x + a, self.y + b))

    def react(self, playerx, playery):
        self.path = []
        dx = playerx - self.x
        dy = playery - self.y
        moves = {(1, 0): (self.x-1, self.y),
                 (-1, 0): (self.x+1, self.y),
                 (0, 1): (self.x, self.y-1),
                 (0, -1): (self.x, self.y+1),
                 (2, 0): (self.x-1, self.y),
                 (-2, 0): (self.x+1, self.y),
                 (0, 2): (self.x, self.y-1),
                 (0, -2): (self.x, self.y+1),
        }
        if (self.x-1, self.y) not in Wall.wallList and 0 <= self.x-1 <= 13 and 0 <= self.y <= 13:
            moves[0, 0] = (self.x-1, self.y)
        elif (self.x, self.y+1) not in Wall.wallList and 0 <= self.x <= 13 and 0 <= self.y+1 <= 13:
            moves[0, 0] = (self.x, self.y+1)
        elif (self.x+1, self.y) not in Wall.wallList and 0 <= self.x+1 <= 13 and 0 <= self.y <= 13:
            moves[0, 0] = (self.x+1, self.y)

        for i in range(-2, 0):
            moves[(1, i)] = (self.x-1, self.y+1)
            moves[(2, i)] = (self.x - 1, self.y + 1)
            moves[(-1, i)] = (self.x+1, self.y+1)
            moves[(-2, i)] = (self.x + 1, self.y + 1)
        for j in range(1, 3):
            moves[(1, j)]= (self.x-1, self.y-1)
            moves[(2, j)] = (self.x - 1, self.y - 1)
            moves[(-1, j)]= (self.x+1, self.y-1)
            moves[(-2, j)] = (self.x + 1, self.y - 1)
        self.neighborfind()
        if (playerx, playery) in self.neighbors:
            self.path.extend(moves[dx, dy])
        self.update()

    def move(self, px, py):  # execute path every tick, but only react every other tick
        self.neighborfind()
        if len(self.path) > 1:
            if 0 <= self.path[0] <= 13 and 0 <= self.path[1] <= 13:
                if (self.path[0], self.y) not in Wall.wallList and (self.x, self.path[1]) not in Wall.wallList and (self.path[0], self.path[1]) not in Wall.wallList: # normal ferret movement
                    self.x = self.path[0]
                    self.y = self.path[1]
                    self.path.pop(0)
                    self.path.pop(0)
                elif (self.path[0], self.path[1]) in Wall.wallList:  # only one is a wall
                    if (self.path[0], self.y) not in Wall.wallList:
                        self.x = self.path[0]
                    elif (self.x, self.path[1]) not in Wall.wallList:
                        self.y = self.path[1]
                    self.path.pop(0)
                    self.path.pop(0)
                else: # diagonal destination where wall impedes one of the cardinal directions
                    if (self.path[0], self.y) in Wall.wallList:
                        if (self.x, self.path[1]) not in Wall.wallList:
                            self.y = self.path[1]
                            self.path.pop(1)
                            self.checkx = True
                    elif (self.x, self.path[1]) in Wall.wallList:
                        if (self.path[0], self.y) not in Wall.wallList:
                            self.x = self.path[0]
                            self.path.pop(0)
                            self.checky = True
            else:
                if 0 <= self.path[0] <= 13 and (self.path[0], self.y) not in Wall.wallList:
                    self.x = self.path[0]
                elif 0 <= self.path[1] <= 13 and (self.x, self.path[1]) not in Wall.wallList:
                    self.y = self.path[1]
                self.path.pop(0)
                self.path.pop(0)

        else: # second direction of last case
            if (px, py) not in self.neighbors:
                if self.checky and (self.x, self.path[0]) not in Wall.wallList:
                    self.y = self.path[0]
                    self.path = []
                elif self.checkx and (self.path[0], self.y) not in Wall.wallList:
                    self.x = self.path[0]
                    self.path = []
                self.checkx = False
                self.checky = False
            else:
                self.path = []
        self.update()

    def update(self):
        self.rect.x = self.x * tilesize
        self.rect.y = self.y * tilesize

class Ferret_pad(pg.sprite.Sprite):
    def __init__(self, game, x, y, color): # green = g, yellow = y, red = r, blue = b, orange = o
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((tilesize, tilesize))
        self.image.fill(purple)
        self.color = color
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.neighbors = []

    def spawnpoints(self):
        for i in range(-4, 5):
            for j in range(-4, 5):
                if 0 <= self.x+i <= 13 and 0 <= self.y+j <= 13 and (self.x+i, self.y+j) not in Wall.wallList:
                    self.neighbors.append((self.x+i, self.y+j))

        for a in range(-1, 2):
            for b in range(-1, 2):
                if (self.x+a, self.y+b) in self.neighbors:
                    self.neighbors.pop(self.neighbors.index((self.x+a, self.y+b)))
        return self.neighbors

    def draw(self):
        pg.draw.rect(self.image, self.color, (0, 0, 32, 32), 15)

    def update(self):
        self.rect.x = self.x*tilesize
        self.rect.y = self.y*tilesize

class Wall(pg.sprite.Sprite):
    wallList = []
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((tilesize, tilesize))
        self.image.fill(wallcolor)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * tilesize
        self.rect.y = y * tilesize
        self.neighbors = []

    def get_neighbors(self):
        self.neighbors = []
        for i in [(self.x + 1, self.y), (self.x - 1, self.y), (self.x, self.y + 1), (self.x, self.y - 1)]:
            if i not in Wall.wallList and i[0] >= 0 and i[0] <= 13 and 0 <= i[1] and i[1] <= 13:
                self.neighbors.append(i)
        return self.neighbors
