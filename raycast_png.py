from math import cos, pi, sin
from PIL import Image

IMAGE_WIDTH = 1024
IMAGE_HEIGHT = 1024

MAP_WIDTH = 16
MAP_HEIGHT = 16
MAP = """
XXXXXXXXXXXXXXXX
X              X
X      X       X
X   XXXXX      X
X   XX         X
X              X
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
MAP = MAP.translate({ord('\n'): None})

# width/height in pixels of each map cell (ie: pixels per cell)
CELL_WIDTH = IMAGE_WIDTH / MAP_WIDTH
CELL_HEIGHT = IMAGE_HEIGHT / MAP_HEIGHT

PLAYER_X = 2
PLAYER_Y = 2
PLAYER_A = 1.57  # radians, ie: bound between 0 and 2 * pi
PLAYER_FOV = pi / 2.0  # radians


class COLOURS(object):
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)


def draw_rectangle(
        frame_buffer,
        image_width,
        image_height,
        x,
        y,
        width,
        height,
        colour,
):
    for i in range(0, width):
        for j in range(0, height):
            cx = x + i
            cy = y + j
            frame_buffer[cx + (cy * image_width)] = colour


def dump_image(frame_buffer, filename, width=IMAGE_WIDTH, height=IMAGE_HEIGHT):
    img = Image.new('RGB', (width, height))
    img.putdata(frame_buffer)
    img.save(filename)


def raycast():
    frame_buffer = [
        COLOURS.WHITE for i in range(0, IMAGE_WIDTH * IMAGE_HEIGHT)
    ]
    for i in range(0, IMAGE_WIDTH):
        left_bound = PLAYER_A - (PLAYER_FOV / 2)  # radians
        right_bound = PLAYER_FOV * (
            i / IMAGE_WIDTH
        )  # radians, ie: find proportion across image, then scale by FOV
        a = left_bound + right_bound
        t = 0.0
        while t < 20.0:
            cx = PLAYER_X + (t * cos(a))
            cy = PLAYER_Y + (t * sin(a))

            pix_x = cx * CELL_WIDTH
            pix_y = cy * CELL_HEIGHT

            if MAP[int(cx) + int(cy) * MAP_WIDTH] != ' ':
                column_height = IMAGE_HEIGHT / (t * cos(a - PLAYER_A))
                is_cell_boundary = ((int(pix_x) % int(CELL_WIDTH) == 0)
                                    or (int(pix_y) % int(CELL_HEIGHT) == 0))
                if is_cell_boundary:
                    colour = COLOURS.WHITE
                else:
                    colour = COLOURS.BLACK
                draw_rectangle(
                    frame_buffer,
                    IMAGE_WIDTH,
                    IMAGE_HEIGHT,
                    x=int(IMAGE_WIDTH / 2 + i),
                    y=int(IMAGE_HEIGHT / 2 - column_height / 2),
                    width=1,
                    height=int(column_height),
                    colour=colour,
                )
                break

            t += 0.05

    dump_image(frame_buffer, filename='test.png')
