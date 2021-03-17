import tcod
from src.interface import Interface
from src.animation import Animation, AnimationFrame
from src.entity.entities import Mobile
from src.entity.landscape import WalkableTerrain, Wall
from src.menus import Menu, MenuOption
from src.sigil import Sigil
from math import floor
from time import time_ns
import multiprocessing as mp

# TODO: Move these to a config file
WIDTH, HEIGHT = 1080, 768
TILESET_SIZE = 16
GAMELOG_HEIGHT = 12
READOUT_WIDTH = 24
#MIN_ROWS, MIN_COLUMNS = 55, 75


#FLAGS = tcod.context.SDL_WINDOW_RESIZABLE | tcod.context.SDL_WINDOW_MAXIMIZED
FLAGS = tcod.context.SDL_WINDOW_FULLSCREEN_DESKTOP


def __time_ms():
    """We're gonna clock the game in milliseconds, so using 1000 * epoch nanoseconds should be fine."""
    return int(time_ns()/1000000)


def main():
    # Make the multiprocessing logic used in the modules happy.
    mp.freeze_support()

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
        interface.new_game_log(height=10, width=40)
        interface.print_to_log("This is a log tests!", color=(25, 250, 25))
        interface.print_to_log("This is an exceptionally long log tests so we can see how well it handles multiples of these.")
        interface.print_to_log("This is another line.")
        interface.print_to_log("This is yet another line.")
        interface.print_to_log("This should bump the first line off of the screen.")
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
    menu.add_option(MenuOption(text="Do More Nothing",
                               width=24, height=5,
                               on_select=lambda x: print("Did more nothing!")))
    menu.add_option(MenuOption(text="Make this menu long",
                               width=24, height=5,
                               on_select=lambda x: print("Did more nothing!")))
    menu.add_option(MenuOption(text="Like REALLY long",
                               width=24, height=5,
                               on_select=lambda x: print("Did more nothing!")))
    menu.add_option(MenuOption(text="Because we, ah...",
                               width=24, height=5,
                               on_select=lambda x: print("Did more nothing!")))
    menu.add_option(MenuOption(text="Need to tests something",
                               width=24, height=5,
                               on_select=lambda x: print("Did more nothing!")))
    menu.add_option(MenuOption(text="You know, uh...",
                               width=24, height=5,
                               on_select=lambda x: print("Did more nothing!")))
    menu.add_option(MenuOption(text="that one thing...",
                               width=24, height=5,
                               on_select=lambda x: print("Did more nothing!")))
    menu.add_option(MenuOption(text="Oh yeah!",
                               width=24, height=5,
                               on_select=lambda x: print("Did more nothing!")))
    menu.add_option(MenuOption(text="Overflow behavior! :)",
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
                interface.playfield.window = (win_width - READOUT_WIDTH,
                                              win_height - GAMELOG_HEIGHT)
            interface.tick()
            interface.print_self()

            # Forward the reference time to the time at which we started this batch of logic
            last_tick = now_ms

if __name__ == "__main__":
    main()
