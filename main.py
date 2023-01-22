import pygame as pg
import sys
import math
import random
import time
from os import path
from settings import *
from sprites import *
from A_Star import *

class Game:
    graph = GridWithWeights(14, 14)
    graph.weights = {}
    graph.walls = []
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((width, height))
        pg.display.set_caption(title)
        self.clock = pg.time.Clock()
        self.load_data()
        self.tickcount = 0
        self.start = None
        self.goal = None
        self.ferrets = []
        self.path = []
        self.current_time = 0


    def load_data(self):
        game_folder = path.dirname(__file__)
        self.map_data = []
        with open(path.join(game_folder, 'map.txt'), 'rt') as f:
            for line in f:
                self.map_data.append(line)

    def new(self):
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        padspawn = random.choice(['r', 'b', 'y', 'o', 'g'])
        for row, tiles in enumerate(self.map_data):
            for col, tile in enumerate(tiles):
                if tile == '#':
                    Wall(self, col, row)
                    self.graph.walls.append((col, row))
                    Wall.wallList.append((col, row))
                elif tile == 'p':
                    self.player = Player(self, col, row)
        for row, tiles in enumerate(self.map_data):
            for col, tile in enumerate(tiles):
                if tile == 'r':
                    red_pad = Ferret_pad(self, col, row, red)
                    red_pad.draw()
                    red_spawn = random.choice(red_pad.spawnpoints())
                    if padspawn == 'r':
                        red_spawn = (red_pad.x, red_pad.y)
                        Wall.wallList.append((red_pad.x, red_pad.y))
                    self.red_ferret = Ferret(self, red_spawn[0], red_spawn[1], red, red_pad)
                    self.ferrets.append(self.red_ferret)
                elif tile == 'b':
                    blue_pad = Ferret_pad(self, col, row, blue)
                    blue_pad.draw()
                    blue_spawn = random.choice(blue_pad.spawnpoints())
                    if padspawn == 'b':
                        blue_spawn = (blue_pad.x, blue_pad.y)
                        Wall.wallList.append((blue_pad.x, blue_pad.y))
                    self.blue_ferret = Ferret(self, blue_spawn[0], blue_spawn[1], blue, blue_pad)
                    self.ferrets.append(self.blue_ferret)
                elif tile == 'y':
                    yellow_pad = Ferret_pad(self, col, row, yellow)
                    yellow_pad.draw()
                    yellow_spawn = random.choice(yellow_pad.spawnpoints())
                    if padspawn == 'y':
                        yellow_spawn = (yellow_pad.x, yellow_pad.y)
                        Wall.wallList.append((yellow_pad.x, yellow_pad.y))
                    self.yellow_ferret = Ferret(self, yellow_spawn[0], yellow_spawn[1], yellow, yellow_pad)
                    self.ferrets.append(self.yellow_ferret)
                elif tile == 'g':
                    green_pad = Ferret_pad(self, col, row, green)
                    green_pad.draw()
                    green_spawn = random.choice(green_pad.spawnpoints())
                    if padspawn == 'g':
                        green_spawn = (green_pad.x, green_pad.y)
                        Wall.wallList.append((green_pad.x, green_pad.y))
                    self.green_ferret = Ferret(self, green_spawn[0], green_spawn[1], green, green_pad)
                    self.ferrets.append(self.green_ferret)
                elif tile == 'o':
                    orange_pad = Ferret_pad(self, col, row, orange)
                    orange_pad.draw()
                    orange_spawn = random.choice(orange_pad.spawnpoints())
                    if padspawn == 'o':
                        orange_spawn = (orange_pad.x, orange_pad.y)
                        Wall.wallList.append((orange_pad.x, orange_pad.y))
                    self.orange_ferret = Ferret(self, orange_spawn[0], orange_spawn[1], orange, orange_pad)
                    self.ferrets.append(self.orange_ferret)

    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(fps)
            self.tickcount += 1
            for i in range(60):
                self.events()
                time.sleep(.01 - 1/3600)
            self.playermove()
            for ferret in self.ferrets:
                if ferret.on_pad():
                    if ferret not in self.graph.walls:
                        self.graph.walls.append((ferret.x, ferret.y))
                if len(ferret.path) > 0:
                    ferret.move(self.player.x, self.player.y)
                if self.tickcount % 2 == 0:
                    if not (ferret.on_pad()):
                        ferret.react(self.player.x, self.player.y)
                if ferret.afraid:
                    ferret.thbbt = True
                    if self.tickcount % 2 == 1:
                        ferret.get_small_neighbors()
                        if (self.player.x, self.player.y) in ferret.smallneighbors:
                            ferret.scare()
                            ferret.path = []
                            self.current_time = self.tickcount
                if self.tickcount - self.current_time >= 3:
                    ferret.thbbt = False
            self.update()
            self.draw()
            for ferret in self.ferrets:
                if ferret.thbbt:
                    self.thbbt(ferret)

    def draw_grid(self):
        for x in range (0, width, tilesize):
            pg.draw.line(self.screen, lightgrey, (x, 0), (x, height))
        for y in range (0, height, tilesize):
            pg.draw.line(self.screen, lightgrey, (0, y), (width, y))

    def update(self):
        self.all_sprites.update()

    def draw(self):
        self.screen.fill(purple)
        self.draw_grid()
        self.all_sprites.draw(self.screen)
        pg.display.flip()

    def quit(self):
        pg.quit()
        sys.exit()

    def moveprep(self, goal):
        mousex = math.floor(goal[0] / tilesize)
        mousey = math.floor(goal[1] / tilesize)
        self.graph.weight_diags((self.player.x, self.player.y))
        self.start = (self.player.x, self.player.y)
        not_ferret = True
        for i in range(len(self.ferrets)):
            if (mousex, mousey) == (self.ferrets[i].x, self.ferrets[i].y):
                not_ferret = False
        if (mousex, mousey) not in self.graph.walls and not_ferret:
            self.goal = (mousex, mousey)
            self.path = self.player.pathfind(self.graph, self.start, self.goal)
        for f in self.ferrets:
            if (mousex, mousey) == (f.x, f.y):
                if pg.mouse.get_pressed()[0]:
                    f.afraid = True
                    lengths = {}
                    f.get_small_neighbors()
                    if len(f.smallneighbors) > 0:
                        for i in f.smallneighbors:
                            self.path = self.player.pathfind(self.graph, self.start, (i[0], i[1]))
                            lengths[len(self.path)] = self.path
                        self.path = lengths[min(lengths)]
                else:
                    self.path = self.player.pathfind(self.graph, self.start, (f.x, f.y))
            else:
                f.afraid = False
        for w in self.walls:
            if (mousex, mousey) == (w.x, w.y):
                lengths = {}
                w.get_neighbors()
                if len(w.neighbors) > 0:
                    for i in w.neighbors:
                        self.path = self.player.pathfind(self.graph, self.start, (i[0], i[1]))
                        lengths[len(self.path)] = self.path
                    self.path = lengths[min(lengths)]
        if len(self.path)%2 == 0:
            self.path = self.path[1::2]
        else:
            temp = self.path[len(self.path)-1]
            self.path = self.path[1::2]
            self.path.append(temp)

    def playermove(self):
        if len(self.path) > 0:
            self.player.x = self.path[0][0]
            self.player.y = self.path[0][1]
            self.path.pop(0)

    def thbbt(self, ferret):
        pg.font.init()
        font = pg.font.SysFont('arial', 20)
        text = font.render('Squeak!', 1, (255, 240, 0))
        if ferret.y == 0 and ferret.x == 0:
            self.screen.blit(text, ((ferret.x) * 32, (ferret.y) * 32))
        elif ferret.y == 0:
            self.screen.blit(text, ((ferret.x) * 32, (ferret.y) * 32))
        elif ferret.x == 0:
            self.screen.blit(text, ((ferret.x) * 32, (ferret.y - 1) * 32))
        elif ferret.x == 13:
            self.screen.blit(text, ((ferret.x-1) * 32, (ferret.y) * 32))
        else:
            self.screen.blit(text, ((ferret.x) * 32, (ferret.y-1)*32))
        pg.display.update()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
            if event.type == pg.MOUSEBUTTONDOWN:
                self.moveprep(pg.mouse.get_pos())
if __name__ == "__main__":
    g = Game()
    while True:
        g.new()
        g.run()
