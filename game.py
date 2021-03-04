import tcod
from src.interface import Interface
from src.animation import Animation, AnimationFrame
from src.entity.entities import Mobile
from src.entity.landscape import WalkableTerrain, Wall
from src.menus import Menu, MenuOption
from src.sigil import Sigil
from math import floor
from time import time_ns

# Default window resolution
WIDTH, HEIGHT = 720, 480
TILESET_SIZE = 16
FLAGS = tcod.context.SDL_WINDOW_RESIZABLE | tcod.context.SDL_WINDOW_MAXIMIZED


def __time_ms():
    """We're gonna clock the game in milliseconds, so using 1000 * epoch nanoseconds should be fine."""
    return int(time_ns()/1000000)


def main():
    # Load the tileset and context
    tileset = tcod.tileset.load_tilesheet("tilesets/yayo_c64_16x16.png", 16, 16,
                                          charmap=tcod.tileset.CHARMAP_CP437)
    context = tcod.context.new(width=WIDTH,
                               height=HEIGHT,
                               tileset=tileset,
                               sdl_window_flags=FLAGS)

    interface = Interface(context)

    # Mock-up of generating the main menu, which should be its own class, I think
    menu = Menu(width=floor(WIDTH/(2*TILESET_SIZE)),
                height=floor(HEIGHT/TILESET_SIZE),
                interface=interface,
                spacing=1)

    def launch_the_game(event):
        interface.new_playfield(width=200,
                                height=80)

        floors = []
        for y in range(0, 40):
            floors.append([(x, y, WalkableTerrain())
                           for x in range(0, 60)])

        for f in sum(floors, []):
            x, y, ent = f
            ent.introduce_at(x, y, interface.playfield)

        walls = [(x, 20, Wall()) for x in range(0, 11)]
        for w in walls:
            x, y, ent = w
            ent.introduce_at(x, y, interface.playfield)

        player_char = Mobile(size=4,
                             sigil=Sigil("@", priority=3),
                             name="Player Character")
        player_char.introduce_at(10, 10, interface.playfield)
        interface.playfield.player_character = player_char

        interface.playfield.origin = (2, 2)
        interface.add_animation(7, 7, Animation(frames=[AnimationFrame(Sigil("\\"), 5),
                                                        AnimationFrame(Sigil("|"), 5),
                                                        AnimationFrame(Sigil("/"), 5),
                                                        AnimationFrame(Sigil("-"), 5)],
                                                repeating=True))
        blue_floor = WalkableTerrain(color=(50, 50, 255))
        blue_floor.sigil = Sigil("!", priority=blue_floor.sigil.priority)
        blue_floor.introduce_at(12, 12, interface.playfield)

        # print(interface.playfield.get_cell(12, 12).sigils)

        menu.close_menu()

    menu.add_option(MenuOption(text="Start Game",
                               width=24, height=5,
                               on_select=launch_the_game))
    menu.add_option(MenuOption(text="Do Nothing",
                               width=24, height=5,
                               on_select=lambda x: print("Did nothing!")))
    menu.add_option(MenuOption(text="Do Nothing Else",
                               width=24, height=5,
                               on_select=lambda x: print("Did more nothing!")))
    interface.open_menu(menu)

    last_tick = __time_ms()  # In epoch milliseconds
    tick_length = 50         # Milliseconds per engine tick
    while True:
        now_ms = __time_ms()

        # Only run the main loop logic if we've reached the next clock increment
        if now_ms - last_tick >= tick_length:
            if interface.playfield:
                win_width, win_height = context.recommended_console_size(min_columns=50,
                                                                         min_rows=40)
                interface.playfield.window = (win_width - 20, win_height - 12)
            interface.tick()
            interface.print_self()

            # Forward the reference time to the time at which we started this batch of logic
            last_tick = now_ms

# def main():
#     # Load the tileset and context
#     tileset = tcod.tileset.load_tilesheet("tilesets/yayo_c64_16x16.png", 16, 16,
#                                           charmap=tcod.tileset.CHARMAP_CP437)
#     context = tcod.context.new(width=WIDTH,
#                                height=HEIGHT,
#                                tileset=tileset,
#                                sdl_window_flags=FLAGS)
#
#     player_char = Mobile(size=4,
#                          sigil=Sigil("@", priority=3),
#                          name="Player Character")
#     #playfield = PlayField(width=)
#
#     # Create an interface
#     interface = Interface(context=context)
#
#     GameLog(45, 12,
#             initial_log=[LogEntry("This is a small log entry"),
#                          LogEntry("This is an obtusely long log entry used in order to try to exceed the maximum line length and thus test word wrapping in the game log.")])
#     menu = Menu(30, 50, menus=interface._menus)
#
#     def _start_the_game(dummy_var):
#         from src.entity.entities import Wall
#         interface.new_playfield(width=60, height=40,
#                                 player_character=player_char,
#                                 player_spawn=(10, 10),
#                                 contents=[(x, 1, Wall())
#                                           for x in range(4, 9)])
#         interface.close_menu(menu)
#
#     menu.add_option(MenuOption("Launch game", width=20, height=3,
#                                on_select=lambda x: _start_the_game(x)))
#     interface.open_menu(menu)
#
#     while True:
#         interface.tick()
#         interface.print_self()


if __name__ == "__main__":
    main()
