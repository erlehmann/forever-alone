#!/usr/bin/python
# -*- coding: utf-8 -*-
import sprite
import pygame.image
import os

import pygame.sprite
import terrain

from random import randint

class Terrain(terrain.Terrain):
    frames = sprite.read_frames(os.path.join("lib", "terrain",
                                                  "building.png"), 16, 16)
    def __init__(self, pos, display, level=None):
        self.image = self.frames[1][1]
        self.level = level
        terrain.Terrain.__init__(self, pos, display, level)

    def update(self):
        x, y = self.pos
        level = self.level

        if (randint(0,6) == 0):
            self.image = self.frames[2][1]  # 

        # roof, upper corners
        if not level.is_building((x-1, y-1)) and \
           not level.is_building((x-1, y)) and \
           not level.is_building((x, y-1)):
            edge = pygame.sprite.Sprite(self.display.shadows)
            edge.rect = pygame.rect.Rect(x*16-16, y*16-16, 16, 16)
            edge.image = self.frames[0][0]

        if not level.is_building((x, y-1)):
            self.image = self.frames[3][1]
            edge = pygame.sprite.Sprite(self.display.shadows)
            edge.rect = pygame.rect.Rect(x*16, y*16-16, 16, 16)
            edge.image = self.frames[1][0]

        if not level.is_building((x+1, y-1)) and \
           not level.is_building((x+1, y)) and \
           not level.is_building((x, y-1)):
            edge = pygame.sprite.Sprite(self.display.shadows)
            edge.rect = pygame.rect.Rect(x*16+16, y*16-16, 16, 16)
            edge.image = self.frames[4][0]

        # side things
        if not level.is_building((x-1, y)):
            edge = pygame.sprite.Sprite(self.display.shadows)
            edge.rect = pygame.rect.Rect(x*16-16, y*16, 16, 16)
            edge.image = self.frames[0][1]

        if not level.is_building((x+1, y)):
            edge = pygame.sprite.Sprite(self.display.shadows)
            edge.rect = pygame.rect.Rect(x*16+16, y*16, 16, 16)
            edge.image = self.frames[4][1]

        # bottom, bottom corners
        if not level.is_building((x-1, y+1)) and \
           not level.is_building((x-1, y)) and \
           not level.is_building((x, y+1)):
            edge = pygame.sprite.Sprite(self.display.shadows)
            edge.rect = pygame.rect.Rect(x*16-16, y*16+16, 16, 16)
            edge.image = self.frames[0][2]

        if not level.is_building((x, y+1)):
            edge = pygame.sprite.Sprite(self.display.shadows)
            edge.rect = pygame.rect.Rect(x*16, y*16+16, 16, 16)
            edge.image = self.frames[1][2]

        if not level.is_building((x+1, y+1)) and \
           not level.is_building((x+1, y)) and \
           not level.is_building((x, y+1)):
            edge = pygame.sprite.Sprite(self.display.shadows)
            edge.rect = pygame.rect.Rect(x*16+16, y*16+16, 16, 16)
            edge.image = self.frames[4][2]
