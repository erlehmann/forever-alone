#!/usr/bin/python
# -*- coding: utf-8 -*-
import sprite
import pygame.image
import os

import pygame.sprite
import terrain

class Terrain(terrain.Terrain):
    frames = sprite.read_frames(os.path.join("lib", "terrain",
                                                  "sidewalk.png"), 16, 16)
    def __init__(self, pos, display, level=None):
        self.image = self.frames[4][1]
        self.level = level
        terrain.Terrain.__init__(self, pos, display, level)

    def update(self):
        x, y = self.pos
        level = self.level

        if level.is_street((x+1, y)):
            # street: E
            if level.is_street((x-1, y)):
                # street: WE
                if level.is_street((x, y+1)):
                    # street: SWE
                    if level.is_street((x, y-1)):
                        # street: NSWE
                        pass
                    else:
                        # street: SWE, no street: N
                        pass
                else:
                    # street: WE, no street: S
                    if level.is_street((x, y-1)):
                        # street: NWE, no street: S
                        pass
                    else:
                        # street: WE, no street: NS
                        pass
            else:
                # street: E, no street: W
                if level.is_street((x, y+1)):
                    # street: SE, no street: W
                    if level.is_street((x, y-1)):
                        # street: NSE, no street: W
                        pass
                    else:
                        # street: SE, no street: NW
                        self.image = self.frames[5][2]
                else:
                    # street: E, no street: SW
                    if level.is_street((x, y-1)):
                        # street: NE, no street: SW
                        self.image = self.frames[5][0]
                    else:
                        # street: E, no street: NSW
                        self.image = self.frames[5][1]
        else:
            # no street: E
            if level.is_street((x-1, y)):
                # street: W, no street: E
                if level.is_street((x, y+1)):
                    # street: SW, no street: E
                    if level.is_street((x, y-1)):
                        # street: NSW, no street: E
                        pass
                    else:
                        # street: SW, no street: NE
                        self.image = self.frames[3][2]
                else:
                    # street: W, no street: SE
                    if level.is_street((x, y-1)):
                        # street: NW, no street: SE
                        self.image = self.frames[3][0]
                    else:
                        # street: W, no street: NSE
                        self.image = self.frames[3][1]
            else:
                # no street: WE
                if level.is_street((x, y+1)):
                    # street S, no street: WE
                    if level.is_street((x, y-1)):
                        # street NS, no street: WE
                        pass
                    else:
                        # street S, no street NWE
                        self.image = self.frames[1][0]
                        
                else:
                    # no street: SWE
                    if level.is_street((x, y-1)):
                        # street: N, no street: SWE
                        self.image = self.frames[1][2]
                    else:
                        # no street: NSWE
                        if level.is_street((x-1, y-1)):
                            # street corner, street is at NW
                            self.image = self.frames[2][2]
                        elif level.is_street((x-1, y+1)):
                            # street corner, street is at SW
                            self.image = self.frames[2][0]
                        elif level.is_street((x+1, y-1)):
                            # street corner, street is at NE
                            self.image = self.frames[0][2]
                        elif level.is_street((x+1, y+1)):
                            # street corner, street is at SE
                            self.image = self.frames[0][0]
