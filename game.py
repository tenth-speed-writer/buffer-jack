import tcod
import src
from math import floor

WIDTH, HEIGHT = 720, 480
TILESET_SIZE = 16
FLAGS = tcod.context.SDL_WINDOW_RESIZABLE | tcod.context.SDL_WINDOW_MAXIMIZED

tileset = tcod.tileset.load_tilesheet("tilesets/yayo_c64_16x16.png", 16, 16,
                                      charmap=tcod.tileset.CHARMAP_CP437)


# def test_menu(context,
#               height: int = 300,
#               width: int = 400):
#     c = context.new_console(order="F")
#     close_menu = False
#     while not close_menu:
#         c.print(5, 1, "This is definitely where the menu goes.")
#         context.present(c)
#
#         for event in tcod.event.get():
#             context.convert_event(event)
#             if event.type == "KEYDOWN" and event.sym == tcod.event.K_ESCAPE:
#                 close_menu = True


# the -> syntax gives a return type, i think?
def main() -> None:
    # console = tcod.Console(width=floor(WIDTH/TILESET_SIZE),
    #                        height=floor(HEIGHT/TILESET_SIZE),
    #                        order="F")

    with tcod.context.new(width=WIDTH,
                          height=HEIGHT,
                          tileset=tileset,
                          title="Buffer Jack",
                          sdl_window_flags=FLAGS) as context:

        # For some reason, a while-true loop will never not feel hacky to me. /AS
        while True:
            console = context.new_console(order="F")

            # Magic for a given console goes between here and context.present
            console.print(5, 3, "Let's keep it quiet, eh?")
            context.present(console=console,
                            integer_scaling=False)

            for event in tcod.event.wait():
                context.convert_event(event)
                console.print(5, 4, str(event))
                context.present(console)

                if event.type == "QUIT":
                    # Nuke it from the OS
                    raise SystemExit()

                if event.type == "WINDOWRESIZED":
                    pass

                if event.type == "KEYDOWN":
                    # Check if it's a movement key.
                    # If the player isn't in a menu, move.
                    print(event)
                    if src.inputs.is_movement_key(event):
                        delta = src.inputs.get_position_delta(event)
                        print("{}, {}".format(str(delta.dx),
                                              str(delta.dy)))
                    # elif event.sym == tcod.event.K_i:
                    #     test_menu(context=context)
                    else:
                        continue


if __name__ == "__main__":
    main()
