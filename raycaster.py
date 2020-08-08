import pygame

from math import cos, pi, sin
from PIL import Image
from typing import Tuple

IMAGE_WIDTH = 1024
IMAGE_HEIGHT = 1024

MAP_LAYOUT = """
XXXXXXXXXXXXXXXX
X              X
X              X
X              X
X              X
X     X        X
X              X
X              X
X              X
X              X
X              X
X              X
X              X
X              X
X              X
XXXXXXXXXXXXXXXX
"""
MAP_LAYOUT = MAP_LAYOUT.translate({ord('\n'): None})

PLAYER_X = 2
PLAYER_Y = 2
PLAYER_VIEW_ANGLE = 1.57
PLAYER_FIELD_OF_VISION = pi / 2.0


class COLOURS(object):
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)


def offset_position_along_angle(position: Tuple[int, int], offset: float, angle: float) -> Tuple[int, int]:
    x, y = position
    return int(x + (offset * cos(angle))), int(y + (offset * sin(angle)))


def draw_player_pov(player, game_map, frame, image_width=IMAGE_WIDTH, image_height=IMAGE_HEIGHT):
    for i in range(0, image_width):
        ray_angle = (player.view_angle - (player.field_of_vision / 2)) + player.field_of_vision * (
            i / image_width
        )
        ray_range = 0.0
        while ray_range < 20.0:  # XXX: why 20?
            ray_map_x, ray_map_y = offset_position_along_angle((player.x_position, player.y_position), ray_range, ray_angle)
            cast_ray_frame_x = ray_map_x * game_map.cell_width
            cast_ray_frame_y = ray_map_y * game_map.cell_height

            if not game_map.is_accessible(ray_map_x, ray_map_y):
                column_height = image_height / (ray_range * cos(ray_angle - player.view_angle))

                is_cell_boundary = i % game_map.cell_width == 0
                if is_cell_boundary:
                    colour = COLOURS.WHITE
                else:
                   colour = COLOURS.BLACK

                left = i
                top = (image_height / 2) - (column_height / 2)
                width = 1
                height = column_height
                rect = (left, top, width, height)
                pygame.draw.rect(frame, colour, rect)
                break

            ray_range += 0.05

class Player(object):

    def __init__(
        self,
        x_position=PLAYER_X,
        y_position=PLAYER_Y,
        player_view_angle=PLAYER_VIEW_ANGLE,
        player_field_of_vision=PLAYER_FIELD_OF_VISION
    ):
        self.x_position = x_position
        self.y_position = y_position
        self.view_angle = player_view_angle
        self.field_of_vision = player_field_of_vision

    def move_forward(self, game_map):
        new_x = self.x_position + 1 * cos(self.view_angle)
        new_y = self.y_position + 1 * sin(self.view_angle)
        if game_map.is_accessible(int(new_x), int(new_y)):
            self.x_position = new_x
            self.y_position = new_y

    def move_backward(self, game_map):
        new_x = self.x_position - 1 * cos(self.view_angle)
        new_y = self.y_position - 1 * sin(self.view_angle)
        if game_map.is_accessible(int(new_x), int(new_y)):
            self.x_position = new_x
            self.y_position = new_y

    def turn_right(self):
        view_angle_normalized = self.view_angle / (2 * pi)
        new_angle_normalized = view_angle_normalized + 0.01
        if new_angle_normalized > 100.0:
            new_angle_normalized = 0.0 + (new_angle_normalized - 100.0)
        self.view_angle = new_angle_normalized * (2 * pi)

    def turn_left(self):
        view_angle_normalized = self.view_angle / (2 * pi)
        new_angle_normalized = view_angle_normalized - 0.01
        if new_angle_normalized < 0.0:
            new_angle_normalized = 100.0 - abs(new_angle_normalized)
        self.view_angle = new_angle_normalized * (2 * pi)


class Map(object):

    def __init__(self, map_layout, map_width, map_height, image_width, image_height):
        self.map_layout = map_layout
        self.map_width = map_width
        self.map_height = map_height
        try:
            assert len(self.map_layout) == self.map_width * self.map_height
        except AssertionError:
            raise InvalidMapError("Map layout not consistent with map dimensions.")

        # width/height in pixels of each map cell (ie: pixels per cell)
        self.cell_width = image_width / map_width
        self.cell_height = image_height / map_height

    def is_accessible(self, map_x, map_y):
        return self.map_layout[map_x + map_y * self.map_width] == ' '


def handle_key_press(pressed, player, game_map):
    if pressed[pygame.K_UP]:
        player.move_forward(game_map)
    elif pressed[pygame.K_DOWN]:
        player.move_backward(game_map)
    elif pressed[pygame.K_LEFT]:
        player.turn_left()
    elif pressed[pygame.K_RIGHT]:
        player.turn_right()


def should_quit():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return True
        elif event.type == pygame.KEYDOWN:
            if (event.key == pygame.K_ESCAPE) or (event.key == pygame.K_q):
                return True


def draw_frame(screen, player, game_map):
    frame = pygame.Surface(screen.get_size())
    frame.fill(COLOURS.WHITE)
    draw_player_pov(player, game_map, frame)
    screen.blit(frame, (0, 0))


def main():
    pygame.init()
    screen = pygame.display.set_mode((IMAGE_WIDTH, IMAGE_HEIGHT))
    screen.fill(COLOURS.WHITE)

    clock = pygame.time.Clock()
    FPS = 60
    playtime = 0.0

    player = Player()
    game_map = Map(
        map_layout=MAP_LAYOUT,
        map_width=16,
        map_height=16,
        image_width=IMAGE_WIDTH,
        image_height=IMAGE_HEIGHT,
    )

    while True:
        if should_quit():
            break

        milliseconds = clock.tick(FPS)
        playtime += milliseconds / 1000.0

        handle_key_press(pygame.key.get_pressed(), player, game_map)
        draw_frame(screen, player, game_map)

        text = f"FPS: {clock.get_fps():.2f}   Playtime: {playtime:.2f}"
        pygame.display.set_caption(text)

        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()
