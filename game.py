import tcod
from src.interface import Interface
from src.interface.game_log import GameLog, LogEntry
from src.playfield import PlayField
from src.entity.entities import Mobile
from src.entity.landscape import WalkableTerrain
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
    return time_ns()*1000


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
    menu = Menu(width=floor(WIDTH/TILESET_SIZE),
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

        player_char = Mobile(size=4,
                             sigil=Sigil("@", priority=3),
                             name="Player Character")
        player_char.introduce_at(10, 10, interface.playfield)
        interface.playfield.player_character = player_char

        interface.playfield.origin = (2, 2)
        menu.close_menu()

    menu.add_option(MenuOption(text="Start Game",
                               width=24, height=5,
                               on_select=launch_the_game))
    interface.open_menu(menu)

    time = __time_ms()
    tick_length = 15  # Milliseconds, a little under 60 FPS
    while True:
        now_ms = __time_ms()

        # Only run the main loop logic if we've reached the next 15ms system tick
        if now_ms - time >= tick_length:
            win_x, win_y = floor(WIDTH / TILESET_SIZE) - 18, floor(HEIGHT/TILESET_SIZE - 18)
            if interface.playfield:
                interface.playfield.window = win_x, win_y
            interface.tick()
            interface.print_self()

        # Reset the reference time to the time at which we started this loop
        time = now_ms

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




# def main():
#     """Launch the main game loop."""
#     # On launch, open the main menu.

#
#     # Create a new window/SDL context
#     with tcod.context.new(width=WIDTH,
#                           height=HEIGHT,
#                           sdl_window_flags=FLAGS,
#                           tileset=tileset) as context:
#         # Render the main menu
#         console = context.new_console(order="F")
#         main_menu = Menu(width=console.width - 2,  # -2 to account for the border we've already drawn
#                          height=console.height - 2)
#
#         main_menu.add_option(MenuOption(text="Launch\nGame",
#                                         width=min(console.width - 6, 14),  # Ideally 14, but shrink to fit if needed.
#                                         height=5,
#                                         on_select=lambda: print("Player clicked the button!"),
#                                         color=(130, 220, 130)))
#         menus: Optional[List[Tuple[int, int, Menu]]] = None  # [(1, 1, main_menu)]
#
#         # The variable which will hold the active playfield
#
#         player_char = Mobile(size=4,
#                              sigil=Sigil("@", color=(200, 200, 255)),
#                              name="Player Character")
#
#         playfield: Optional[PlayField] = PlayField(200, 200)
#
#         player_char.introduce_at(10, 10, playfield)
#         playfield.dispatch = GameplayHandler(playfield, player_char)
#
#         room = RectangularRoom(30, 20)
#         room.add_door(0, 6)
#         room.add_to_playfield(5, 5, playfield)
#
#         while True:
#             # Create the console and draw
#             console = context.new_console(order="F", min_columns=32, min_rows=24)
#             console.draw_frame(x=0, y=0,
#                                width=console.width,
#                                height=console.height,
#                                title="BUFFER.JACK()")
#
#             # Render the playfield, if one is open
#             if playfield:
#                 # First, tick the contents of the playfield--if we're not waiting on player input.
#                 if player_char.cooldown:  # If it's not zero, else we're gonna hold off.
#                     playfield.tick()
#
#                 # Give it its renderable space--right now everything except the game screen border
#                 playfield.origin = (1, 1)
#                 playfield.window = (console.width - 2,
#                                     console.height - 2)
#
#                 # Get its drawables and print them to console
#                 pf_rows: List[Dict] = playfield.drawables(center_on=player_char.position)
#                 for r in pf_rows:  # Each element is a dictionary with the necessary values
#                     console.print(x=r["x"] + 1,
#                                   y=r["y"] + 1,
#                                   string=r["character"],
#                                   fg=r["rgb"])
#
#             if menus:
#                 # Render each menu that's currently open
#                 for _x, _y, _menu in menus:
#                     _menu.render_menu(_x, _y, console)
#                 top_menu = menus[-1][2]  # The topmost menu will be third element of the last tuple in the list
#                 dispatcher: tcod.event.EventDispatch = top_menu.dispatch
#
#                 # Hand event control to the last
#                 for event in tcod.event.get():
#                     dispatcher.dispatch(event)
#             else:
#                 # If no menu is open, but the playfield is, then use its event handler
#                 dispatcher: tcod.event.EventDispatch = playfield.dispatch
#
#             context.present(console)  # This is where we actually display what we've rendered.
#
#             for event in tcod.event.get():
#                 context.convert_event(event)  # Converting the event fills in mouse event tile coordinates
#                 dispatcher.dispatch(event)    # Pass it along to the appropriate dispatcher
#
#
#
#         # HANDLING MENUS:
#         # Draw each menu on top of one another for each menu in a menus variable,
#         # then pass control of the handler to that menu's handler


if __name__ == "__main__":
    main()
