import pygame
from pygame.locals import *
import os
import re

import item
import monster

class Level(object):
    def __init__(self):
        self.items = []
        self.monsters = []
        self.terrain = []

    def is_floor(self, pos):
        """Used by the wall tiles to tell whether neighbouring
           squares contain floor tiles.
        """
        return not self.is_blocked(pos)

    def is_blocked(self, pos):
        """Used by the creatures to check whether they can move there"""
        x, y = pos
        if x < 0 or y < 0:
            return True
        try:
            return self.blocking[y][x]
        except IndexError:
            return True

    def is_terrain(self, pos, terrain):
        content = self.get_content(pos)
        return terrain in content

    def is_building(self, pos):
        return self.is_terrain(pos, "terrain.building")

    def is_street(self, pos):
        return self.is_terrain(pos, "terrain.street")

    def is_sidewalk(self, pos):
        return self.is_terrain(pos, "terrain.sidewalk")

class StaticLevel(Level):
    def __init__(self):
        self.static_map()
        self.place_monsters(self.map)

    def place_monsters(self, m):
        """Place monsters on the map."""

        self.monsters = {}
        self.items = {}
        for y, line in enumerate(m):
            for x, tile in enumerate(line):
                urls = self.map_key[tile]
                if urls:
                    for url in urls[1:]:
                        kind, name = url.split(".", 1)
                        if kind == "monster":
                            m = monster.create(self, (x, y), name)
                            if name == 'player':
                                self.player = m
                            m.place((x, y))
                        elif kind == "item":
                            i = item.create(self, name)
                            i.place((x, y))
                        elif kind == "status":
                            self.monsters[(x, y)].add_status(name)

    def static_map(self):
        """A mockup of a level map."""
        self.map_key = {
            "X": ("terrain.building",),
            "*": ("terrain.cliff",),
            ":": ("terrain.sidewalk",),
            ".": ("terrain.street",),
            ",": ("terrain.corridor",),
            "O": ("terrain.sidewalk", "monster.eye"),
            "S": ("terrain.sidewalk", "monster.skeleton"),
            "M": ("terrain.sidewalk", "monster.jello"),
            "Z": ("terrain.sidewalk", "monster.zombie"),
            "R": ("terrain.street", "monster.robot"),
            "B": ("terrain.sidewalk", "monster.beast", "status.asleep"),
            "C": ("terrain.sidewalk", "monster.cat"),
            "E": ("terrain.sidewalk", "monster.eisenhower"),
            "V": ("terrain.sidewalk", "monster.bat"),
            "@": ("terrain.sidewalk", "monster.player", "item.up"),
            "&": ("terrain.sidewalk", "item.box"),
            "c": ("terrain.sidewalk", "item.car"),
            "%": ("terrain.sidewalk", "item.chest"),
            "/": ("terrain.sidewalk", "item.wrench"),
            "!": ("terrain.sidewalk", "item.hammer"),
            "~": ("terrain.sidewalk", "item.chainsaw"),
            "+": ("terrain.sidewalk", "item.firstaid"),
            ">": ("terrain.sidewalk", "item.down"),
        }
        self.map = (
            "XXXXXXXXXXXXXXXXXXXXXXXXXX",
            "XXXXXXXXXX::::::XXX::::::X",
            "XX::::XXXX:::R::X..::M:::X",
            "XX:V::XXXX::V:::X.*::::::X",
            "XX::::XXXX::::::X.*::::::X",
            "XX~:::....::/:::..*::::::X",
            "XX::::XXXX::::::***:::Z::X",
            "XXX:::XXXXXXX.*****::::::X",
            "XXX:::XXXXXXX.*******.XXXX",
            "XXX::.XXXX:%:::::****.XXXX",
            "X::::@::..::+::::**:::::XX",
            "X:..::::..::V:E::..::!::XX",
            "X:..::::.....:>::XXO::::XX",
            "::..:c:::::::::::XX:::&:XX",
            "..............XXXXX:::::XX",
            "..............XXXXX:::::XX",
            "::..:::::::::.XXXXXXXX.XXX",
            "X:..:XXXXXXX..XXXXXXXX.XXX",
            "X:..:XXXXXXX.XXXXXXX:::::X",
            "X::::XXXXX::::XXXXXX::%::X",
            "X::::::...::::XXXXXX:::::X",
            "X::::::XXX::::....XX::S::X",
            "XC:::::XXX::B:XXX.XX:::::X",
            "X::::::XXXXXXXXXX...:::::X",
            "X::::M:XXXXXXXXXXXXX:::::X",
            "XXXXXXXXXXXXXXXXXXXXXXXXXX",
        )
        self.blocking = []
        self.terrain = []
        self.w = 0
        for line in self.map:
            block_line = []
            for char in line:
                if char in self.map_key:
                    block_line.append(char in 'X*')
            if self.w < len(block_line):
                self.w = len(block_line)
            self.blocking.append(block_line)
        self.h = len(self.map)

    def get_content(self, pos):
        """List all objects on given map square"""
        x, y = pos
        if x < 0 or y < 0:
            return ()
        try:
            m = self.map[y][x]
        except IndexError:
            return ()
        return self.map_key.get(m, ())
