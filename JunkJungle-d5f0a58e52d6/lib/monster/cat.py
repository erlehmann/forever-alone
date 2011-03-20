#!/usr/bin/python
# -*- coding: utf-8 -*-

import random
import monster
import sprite
import util

class Mob(monster.Monster):
    name = "cat"
    max_hp = 4

    def act(self, level):
        player = self.level.player
        dirs = util.dir_of(self.pos, player.pos)
        for direction in dirs:
            try:
                try:
                    self.walk(direction)
                    return
                except monster.MoveBump, e:
                    if e.monster == player:
                        self.attack(direction, e.monster)
                        return
            except monster.MoveError:
                pass

    class Sprite(sprite.Monster):
        def __init__(self, monster, display):
            sprite.Monster.__init__(self, monster, display)

        def animate(self, delay=1, frames=None):
            """Cat has more frames and facing."""
            sprite.Monster.animate(self, delay, self.frames[self.facing-1])

        def anim_stand(self):
            """Cat is not animated when standing."""
            self.image = self.frames[self.facing-1][0]
            yield None

        def anim_walk(self):
            dx = util.delta_x[self.facing]*2
            dy = util.delta_y[self.facing]*2
            self.move(dx, dy)
            steps = 7
            for step in range(steps):
                self.move(dx, dy)
                self.animate()
                yield None
