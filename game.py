import tcod
import src
from math import floor

WIDTH, HEIGHT = 720, 480
TILESET_SIZE = 16
FLAGS = tcod.context.SDL_WINDOW_RESIZABLE | tcod.context.SDL_WINDOW_MAXIMIZED


# the -> syntax gives a return type, i think?
def main() -> None:
    tileset = tcod.tileset.load_tilesheet("tilesets/yayo_c64_16x16.png", 16, 16,
                                          tcod.tileset.CHARMAP_CP437)

    console = tcod.Console(width=floor(WIDTH/TILESET_SIZE),
                           height=floor(HEIGHT/TILESET_SIZE),
                           order="F")

    with tcod.context.new(width=WIDTH,
                          height=HEIGHT,
                          tileset=tileset,
                          title="Buffer Jack",
                          sdl_window_flags=FLAGS) as context:

        # For some reason, a while-true loop will never not feel hacky to me. /AS
        while True:
            console = context.new_console(order="F")

            # Magic for a given console goes between here and context.present

            context.present(console=console,
                            integer_scaling=True)

            for event in tcod.event.wait():
                context.convert_event(event)
                #79print("Event: {}".format(str(event)))

                if event.type == "QUIT":
                    # Nuke it from the OS
                    raise SystemExit()

                if event.type == "WINDOWRESIZED":
                    pass

                if event.type == "KEYDOWN":
                    # Check if it's a movement key.
                    # If the player isn't in a menu, move.
                    if src.inputs.is_movement_key(event):
                        delta = src.inputs.get_position_delta(event)
                        print("{}, {}".format(str(delta.dx),
                                              str(delta.dy)))
                    else:
                        pass


if __name__ == "__main__":
    main()
