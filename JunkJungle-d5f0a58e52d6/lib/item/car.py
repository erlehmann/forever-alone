#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

import sprite
import item

class Item(item.Item):
    name = "car"
    can_pick = False
    can_push = False
    block = True
