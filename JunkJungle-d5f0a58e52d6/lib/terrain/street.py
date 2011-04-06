#!/usr/bin/python
# -*- coding: utf-8 -*-
import sprite
import pygame.image
import os

import terrain

class Terrain(terrain.Terrain):
    frames = sprite.read_frames(os.path.join("lib", "terrain",
                                                  "street.png"), 16, 16)
    def __init__(self, pos, display, level=None):
        self.image = self.frames[0][0]
        self.level = level
        terrain.Terrain.__init__(self, pos, display, level)

    def update(self):
        x, y = self.pos
        level = self.level

        # vertical crossing
        if (x%11 == 1):
            # ensure street is not a dead end
            if level.is_street((x-1, y)) and \
               level.is_street((x-2, y)) and \
               level.is_street((x+1, y)) and \
               level.is_street((x+2, y)):
                if (level.is_sidewalk((x-1, y-1)) and \
                    level.is_sidewalk((x, y-1)) and \
                    level.is_sidewalk((x+1, y-1)) and \
                    level.is_street((x, y+1)) and \
                    level.is_sidewalk((x-1, y+2)) and \
                    level.is_sidewalk((x, y+2)) and \
                    level.is_sidewalk((x+1, y+2))) or \
                   (level.is_sidewalk((x-1, y+1)) and \
                    level.is_sidewalk((x, y+1)) and \
                    level.is_sidewalk((x+1, y+1)) and \
                    level.is_street((x, y-1)) and \
                    level.is_sidewalk((x-1, y-2)) and \
                    level.is_sidewalk((x, y-2)) and \
                    level.is_sidewalk((x+1, y-2))):
                    self.image = self.frames[1][0]

        # horizontal crossing
        if (y%11 == 5):
            # ensure street is not a dead end
            if level.is_street((x, y-1)) and \
               level.is_street((x, y-2)) and \
               level.is_street((x, y+1)) and \
               level.is_street((x, y+2)):
                if (level.is_sidewalk((x-1, y-1)) and \
                    level.is_sidewalk((x-1, y)) and \
                    level.is_sidewalk((x-1, y+1)) and \
                    level.is_street((x+1, y)) and \
                    level.is_sidewalk((x+2, y-1)) and \
                    level.is_sidewalk((x+2, y)) and \
                    level.is_sidewalk((x+2, y+1))) or \
                   (level.is_sidewalk((x+1, y-1)) and \
                    level.is_sidewalk((x+1, y)) and \
                    level.is_sidewalk((x+1, y+1)) and \
                    level.is_street((x-1, y)) and \
                    level.is_sidewalk((x-2, y-1)) and \
                    level.is_sidewalk((x-2, y)) and \
                    level.is_sidewalk((x-2, y+1))):
                    self.image = self.frames[2][0]
                    
    
