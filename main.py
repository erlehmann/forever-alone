#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
forever alone — a game about loneliness and a city

@copyright: 2008, 2009 Radomir Dopieralski <qq@sheep.art.pl>; 2011 Nils Dagsson Moskopp <nils@dieweltistgarnichtso.net>
@license: GPL, version 3 or (at your option) any later version.

Code by Radomir Dopieralski was originally licensed under BSD, see COPYING for details.
"""

import ConfigParser

import pygame
import pygame.locals as pg

import itertools
import math

# Motion offsets for particular directions
#     N  E  S   W
DX = [0, 1, 0, -1]
DY = [-1, 0, 1, 0]

# Dimensions of the map tiles
MAP_TILE_WIDTH, MAP_TILE_HEIGHT = 5, 5

# Upscaling
SCALE = 8

# Display mode
DISPLAY_MODE = pygame.FULLSCREEN

def GET_DISPLAY_X():
    return pygame.display.Info().current_w

def GET_DISPLAY_Y():
    return pygame.display.Info().current_h

# Clipping area (actual game interface)
CLIP_WIDTH, CLIP_HEIGHT = 80 * SCALE, 60 * SCALE

def GET_CLIP_RECT():
    return pygame.Rect(
        (GET_DISPLAY_X() / 2) - (CLIP_WIDTH / 2),
        (GET_DISPLAY_Y() / 2) - (CLIP_HEIGHT / 2),
        CLIP_WIDTH,
        CLIP_HEIGHT
    )

# Scrolling offsets
OFFSET_X, OFFSET_Y = 0, 0


class ImageCache:
    """Load an image lazily into global cache"""

    def __init__(self):
        self.cache = {}

    def __getitem__(self, filename):
        """Return a file, load it from disk, if needed."""

        try:
            return self.cache[filename]
        except KeyError:
            image = pygame.image.load(filename).convert()
            self.cache[filename] = image
            return image


class TileCache:
    """Load the tilesets lazily into global cache"""

    def __init__(self,  width=MAP_TILE_WIDTH, height=None):
        self.width = width
        self.height = height or width
        self.cache = {}

    def __getitem__(self, filename):
        """Return a table of tiles, load it from disk if needed."""

        key = (filename, self.width, self.height)
        try:
            return self.cache[key]
        except KeyError:
            tile_table = self._load_tile_table(filename, self.width,
                                               self.height)
            self.cache[key] = tile_table
            return tile_table

    def _load_tile_table(self, filename, width, height):
        """Load an image and split it into tiles."""

        image = pygame.image.load(filename).convert()
        image_width, image_height = image.get_size()
        tile_table = []
        for tile_x in range(0, image_width/width):
            line = []
            tile_table.append(line)
            for tile_y in range(0, image_height/height):
                rect = (tile_x*width, tile_y*height, width, height)
                rectsurface = image.subsurface(rect)
                rectsurface = pygame.transform.scale(rectsurface, (height*SCALE, width*SCALE))
                line.append(rectsurface)

        return tile_table


class Lights(pygame.sprite.RenderUpdates):
    """A sprite group that blits additive."""

    def draw(self, surface):
       spritedict = self.spritedict
       surface_blit = surface.blit
       dirty = self.lostsprites
       self.lostsprites = []
       dirty_append = dirty.append
       for s in self.sprites():
           r = spritedict[s]
           newrect = surface_blit(s.image, s.rect, special_flags=pg.BLEND_ADD)
           if r is 0:
               dirty_append(newrect)
           else:
               if newrect.colliderect(r):
                   dirty_append(newrect.union(r))
               else:
                   dirty_append(newrect)
                   dirty_append(r)
           spritedict[s] = newrect
       return dirty


class Light(pygame.sprite.Sprite):
    """Sprite for lights."""

    def __init__(self, filename, owner):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(IMAGE_CACHE[filename], \
            (5 * MAP_TILE_WIDTH * SCALE, 5 * MAP_TILE_HEIGHT * SCALE))
        self.rect = self.image.get_rect()
        self.owner = owner

    def update(self, *args):
        """Make the light follow its owner."""

        self.rect.center = self.owner.rect.midbottom


class SortedUpdates(pygame.sprite.RenderUpdates):
    """A sprite group that sorts them by depth."""

    def sprites(self):
        """The list of sprites in the group, sorted by depth."""

        return sorted(self.spritedict.keys(), key=lambda sprite: sprite.depth)


class Sprite(pygame.sprite.Sprite):
    """Sprite for animated items and base class for Player."""

    is_player = False

    def __init__(self, pos=(0, 0), frames=None):
        super(Sprite, self).__init__()
        if frames:
            self.frames = frames
        self.image = self.frames[0][0]
        self.rect = self.image.get_rect()
        self.animation = self.stand_animation()
        self.pos = pos

    def _get_pos(self):
        """Check the current position of the sprite on the map."""

        return \
            int(round((self.rect.midbottom[0] - (MAP_TILE_WIDTH/2) - OFFSET_X) / (MAP_TILE_WIDTH * SCALE))), \
            int(round((self.rect.midbottom[1] - (MAP_TILE_HEIGHT/2) - OFFSET_Y) / (MAP_TILE_HEIGHT * SCALE)))


    def _set_pos(self, pos):
        """Set the position and depth of the sprite on the map."""

        self.rect.midbottom = \
            (pos[0] * MAP_TILE_WIDTH + (MAP_TILE_WIDTH/2 - 0.5 + OFFSET_X)) * SCALE, \
            (pos[1] * MAP_TILE_HEIGHT + MAP_TILE_HEIGHT/2 + OFFSET_Y) * SCALE
        self.depth = self.rect.midbottom[1]

    pos = property(_get_pos, _set_pos)

    def move(self, dx, dy):
        """Change the position of the sprite on screen."""

        self.rect.move_ip(dx * MAP_TILE_WIDTH, dy * MAP_TILE_HEIGHT)
        self.depth = self.rect.midbottom[1]

    def stand_animation(self):
        """The default animation."""

        while True:
            # Change to next frame every two ticks
            for frame in self.frames[0]:
                self.image = frame
                yield None
                yield None

    def update(self, *args):
        """Run the current animation."""

        self.animation.next()


class Player(Sprite):
    """ Display and animate the player character."""

    is_player = True

    def __init__(self, pos=(1, 1)):
        self.frames = SPRITE_CACHE["player.png"]
        Sprite.__init__(self, pos)
        self.direction = 2
        self.animation = None
        self.image = self.frames[self.direction][0]

    def walk_animation(self):
        """Animation for the player walking."""

        def move_scaled(direction):
            self.move(DX[direction] * SCALE/8, DY[direction] * SCALE/8)

        # This animation is hardcoded for 4 frames
        for frame in range(4):
            self.image = self.frames[self.direction][frame]
            yield None
            move_scaled(self.direction)
            yield None
            move_scaled(self.direction)

    def update(self, *args):
        """Run the current animation or just stand there if no animation set."""

        if self.animation is None:
            self.image = self.frames[self.direction][0]
        else:
            try:
                self.animation.next()
            except StopIteration:
                self.animation = None

class Level(object):
    """Load and store the map of the level, together with all the items."""

    def __init__(self, filename="level.map"):
        self.tileset = ''
        self.map = []
        self.items = {}
        self.key = {}
        self.width = 0
        self.height = 0
        self.load_file(filename)

    def load_file(self, filename="level.map"):
        """Load the level from specified file."""

        parser = ConfigParser.ConfigParser()
        parser.read(filename)
        self.tileset = parser.get("level", "tileset")
        self.map = parser.get("level", "map").split("\n")
        for section in parser.sections():
            if len(section) == 1:
                desc = dict(parser.items(section))
                self.key[section] = desc
        self.width = len(self.map[0])
        self.height = len(self.map)
        for y, line in enumerate(self.map):
            for x, c in enumerate(line):
                if not self.is_wall(x, y) and 'sprite' in self.key[c]:
                    self.items[(x, y)] = self.key[c]

    def render(self):
        """Draw the level on the surface."""

        sidewalk = self.is_sidewalk
        wall = self.is_wall
        tiles = MAP_CACHE[self.tileset]
        image = pygame.Surface((self.width*MAP_TILE_WIDTH*SCALE, self.height*MAP_TILE_HEIGHT*SCALE))
        overlays = {}
        for map_y, line in enumerate(self.map):
            for map_x, c in enumerate(line):
                if sidewalk(map_x, map_y):
                    tile = 3, 1

                    # corner cases
                    if wall(map_x-1, map_y-1):  # corner NW
                        tile = 6, 2

                    if wall(map_x+1, map_y-1):  # corner NE
                        tile = 4, 2

                    if wall(map_x-1, map_y+1):  # corner SW
                        tile = 6, 0

                    if wall(map_x+1, map_y+1):  # corner SW
                        tile = 4, 0

                    # Draw different tiles depending on neighbourhood
                    if wall(map_x, map_y-1):  # wall N
                        tile = 1, 0
                        if wall(map_x-1, map_y):  # wall NW
                            tile = 0, 0
                        if wall(map_x+1, map_y):  # wall NE
                            tile = 2, 0

                    else:  # no wall N
                        if wall(map_x, map_y+1):  # wall S
                            tile = 1, 2
                            if wall(map_x-1, map_y):  # wall SW
                                tile = 0, 2
                            if wall(map_x+1, map_y):  # wall SE
                                tile = 2, 2

                        else:  # no wall N, no wall S
                            if wall(map_x-1, map_y):  # wall W
                                tile = 0, 1
                            if wall(map_x+1, map_y):  # wall E
                                tile = 2, 1

                else:
                    try:
                        tile = self.key[c]['tile'].split(',')
                        tile = int(tile[0]), int(tile[1])
                    except (ValueError, KeyError):
                        # Default to ground tile
                        tile = 0, 3
                tile_image = tiles[tile[0]][tile[1]]
                image.blit(tile_image,
                           (map_x*MAP_TILE_WIDTH*SCALE, map_y*MAP_TILE_HEIGHT*SCALE))
        return image, overlays

    def get_tile(self, x, y):
        """Tell what's at the specified position of the map."""

        try:
            char = self.map[y][x]
        except IndexError:
            return {}
        try:
            return self.key[char]
        except KeyError:
            return {}

    def get_bool(self, x, y, name):
        """Tell if the specified flag is set for position on the map."""

        value = self.get_tile(x, y).get(name)
        return value in (True, 1, 'true', 'yes', 'True', 'Yes', '1', 'on', 'On')

    def is_sidewalk(self, x, y):
        """Is this a sidewalk?"""

        return self.get_bool(x, y, 'sidewalk')

    def is_wall(self, x, y):
        """Is there a wall?"""

        return self.get_bool(x, y, 'wall')

    def is_blocking(self, x, y):
        """Is this place blocking movement?"""

        if not 0 <= x < self.width or not 0 <= y < self.height:
            return True
        return self.get_bool(x, y, 'block')


class Game:
    """The main game object."""

    def __init__(self):
        self.screen = pygame.display.get_surface()
        self.screen.set_clip(GET_CLIP_RECT())

        self.spritebg = self.screen.copy()
        self.pressed_key = None
        self.title_screen = True
        self.game_over = False
        self.lights = Lights()
        self.sprites = SortedUpdates()
        self.overlays = pygame.sprite.RenderUpdates()
        self.use_level(Level())

        pygame.mouse.set_visible(False)

    def intro(self):
        titlescreen = pygame.transform.scale(IMAGE_CACHE["title.png"], (CLIP_WIDTH, CLIP_HEIGHT))
        self.screen.blit(titlescreen, GET_CLIP_RECT())
        pygame.display.update(GET_CLIP_RECT())

        pygame.mixer.init()
        self.trafficsound = pygame.mixer.Sound("traffic.oga")
        self.trafficsound.play()
        self.trafficsound.set_volume(0.2)
        self.trafficsound.fadeout(300000)

        clock = pygame.time.Clock()

        while self.title_screen:
            clock.tick(30)
            event = pygame.event.wait()
            if event.type == pg.KEYDOWN:
                self.title_screen = False

    def use_level(self, level):
        """Set the level as the current one."""

        self.mask = pygame.transform.scale(IMAGE_CACHE["mask.png"], (CLIP_WIDTH, CLIP_HEIGHT))

        self.lights = Lights()
        self.sprites = SortedUpdates()
        self.overlays = pygame.sprite.RenderUpdates()
        self.level = level
        # Populate the game with the level's objects
        for pos, tile in level.items.iteritems():
            if tile.get("player") in ('true', '1', 'yes', 'on'):
                sprite = Player(pos)
                self.player = sprite
            else:
                sprite = Sprite(pos, TileCache()[tile["sprite"]])
            self.sprites.add(sprite)

            if tile.get("light") in ('true', '1', 'yes', 'on'):
                self.lights.add(Light("light.png", sprite))
        # Render the level map
        self.background, overlays = self.level.render()
        # Add the overlays for the level map
        for (x, y), image in overlays.iteritems():
            overlay = pygame.sprite.Sprite(self.overlays)
            overlay.image = image
            overlay.rect = image.get_rect().move(
                x*MAP_TILE_WIDTH* SCALE,
                y*MAP_TILE_HEIGHT* SCALE - (MAP_TILE_HEIGHT/2 * SCALE)
            )

    def control(self):
        """Handle the controls of the game."""

        keys = pygame.key.get_pressed()

        def pressed(key):
            """Check if the specified key is pressed."""

            return self.pressed_key == key or keys[key]

        def walk(d):
            """Start walking in specified direction."""

            x, y = self.player.pos
            self.player.direction = d
            if not self.level.is_blocking(x+DX[d], y+DY[d]):
                self.player.animation = self.player.walk_animation()

        if pressed(pg.K_UP):
            walk(0)
        elif pressed(pg.K_DOWN):
            walk(2)
        elif pressed(pg.K_LEFT):
            walk(3)
        elif pressed(pg.K_RIGHT):
            walk(1)
        elif pressed(pg.K_ESCAPE):
            pygame.event.post(pygame.event.Event(pg.QUIT))
        self.pressed_key = None


    def scroll(self, dx, dy):
        global OFFSET_X, OFFSET_Y
        OFFSET_X += dx
        OFFSET_Y += dy

        self.screen.blit(self.background, (OFFSET_X, OFFSET_Y))

        sprites = itertools.chain(self.sprites, self.overlays)
        for sprite in sprites:
            sprite.rect.move_ip(dx, dy)


    def scroll_after(self, rect):
        dx, dy = 0, 0

        clip = GET_CLIP_RECT()

        if rect.left < clip.left + (5 * MAP_TILE_WIDTH * SCALE):
            dx = 1
            if rect.left < clip.left + (4 * MAP_TILE_WIDTH * SCALE):
                dx = 2

        if rect.top < clip.top + (4 * MAP_TILE_HEIGHT * SCALE):
            dy = 1
            if rect.top < clip.top + (3 * MAP_TILE_HEIGHT * SCALE):
                dy = 2

        if rect.right > clip.right - (5 * MAP_TILE_WIDTH * SCALE):
            dx = -1
            if rect.right > clip.right - (4 * MAP_TILE_WIDTH * SCALE):
                dx = -2

        if rect.bottom > clip.bottom - (4 * MAP_TILE_HEIGHT * SCALE):
            dy = -1
            if rect.bottom > clip.bottom - (3 * MAP_TILE_HEIGHT * SCALE):
                dy = -2

        if dx or dy:
            self.scroll(dx * MAP_TILE_WIDTH/4, dy * MAP_TILE_HEIGHT/4)
            return True

        return False


    def main(self):
        """Run the main loop."""

        clock = pygame.time.Clock()

        firstiteration = True

        # The main game loop
        while not self.game_over:
            scrolled = self.scroll_after(self.player.rect)

            # Ugly and CPU-intensive hack to prevents sprite/mask flickering
            # when moving the player around the screen without scrolling.
            if not scrolled and self.player.animation:
                self.screen.blit(self.background, (OFFSET_X, OFFSET_Y))

            # Don't clear overlays, only sprites.
            # Ugly hack for correct sprite backgrounds.
            self.spritebg.blit(self.background, (OFFSET_X, OFFSET_Y))
            self.lights.clear(self.screen, self.spritebg)
            self.sprites.clear(self.screen, self.spritebg)
            self.sprites.update()
            # If the player's animation is finished, check for keypresses
            if self.player.animation is None:
                self.control()
                self.player.update()
            self.lights.update()

            dirty = self.lights.draw(self.screen)
            dirty.extend(self.sprites.draw(self.screen))
            # Don't add overlays to dirty rectangles, only the places where
            # sprites are need to be updated, and those are already dirty.
            self.overlays.draw(self.screen)

            self.screen.blit(self.mask, GET_CLIP_RECT(), special_flags=pg.BLEND_SUB)

            if scrolled or firstiteration:
                # Draw fucking everything
                dirty = [GET_CLIP_RECT()]
                firstiteration = False

            # Update the dirty areas of the screen
            pygame.display.update(dirty)

            # Wait for one tick of the game clock
            clock.tick(15)
            # Process pygame events
            for event in pygame.event.get():
                if event.type == pg.QUIT:
                    self.game_over = True
                elif event.type == pg.KEYDOWN:
                    self.pressed_key = event.key


if __name__ == "__main__":
    IMAGE_CACHE = ImageCache()
    SPRITE_CACHE = TileCache()
    MAP_CACHE = TileCache(MAP_TILE_WIDTH, MAP_TILE_HEIGHT)

    pygame.init()
    pygame.display.set_mode((GET_DISPLAY_X(), GET_DISPLAY_Y()), DISPLAY_MODE)

    G = Game()
    G.intro()
    G.main()
