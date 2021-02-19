import tcod
import src
from typing import List, Dict
from math import floor

import src.entity.entities as entities

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


def _print_drawables(drawables: List[Dict],
                     console: tcod.console.Console):
    for el in drawables:
        console.print(x=el["x"],
                      y=el["y"],
                      string=el["character"],
                      fg=el["rgb"])


def main() -> None:
    with tcod.context.new(width=WIDTH,
                          height=HEIGHT,
                          tileset=tileset,
                          title="Buffer Jack",
                          sdl_window_flags=FLAGS) as context:

        #TODO: Remove test contents and generate the main menu
        # game_pf = src.playfield.PlayField(width=floor(WIDTH/TILESET_SIZE),
        #                                   height=floor(HEIGHT/TILESET_SIZE),
        #                                   contents=((0, 0, entities.Barricade()),
        #                                             (0, 1, entities.Barricade()),
        #                                             (0, 2, entities.Barricade()),
        #                                             (1, 0, entities.Barricade()),
        #                                             (1, 2, entities.Barricade()),
        #                                             (2, 0, entities.Barricade()),
        #                                             (2, 2, entities.Barricade()),
        #                                             (3, 0, entities.Barricade()),
        #                                             (3, 2, entities.Barricade()),
        #                                             (3, 1, entities.Barricade()),
        #                                             (4, 0, entities.Barricade()),
        #                                             (4, 1, entities.Barricade()),
        #                                             (4, 1, entities.Barricade()),
        #                                             (4, 2, entities.Barricade())
        #                                             ))
        game_pf = src.playfield.PlayField(width=floor(WIDTH / TILESET_SIZE),
                                          height=floor(HEIGHT / TILESET_SIZE),
                                          contents=((0, 0, entities.Barricade()),
                                                    (0, 1, entities.Barricade())))

        player_entity = src.entity.entities.Mobile(size=3,
                                                   sigil=src.sigil.Sigil("@"),
                                                   name="Player Character")
        player_entity.introduce_at(2, 2, game_pf)

        # For some reason, a while-true loop will never not feel hacky to me. /Arima
        while True:
            console = context.new_console(order="F")

            # Magic for a given console goes between here and context.present
            #console.print(5, 3, "Let's keep it quiet, eh?")
            game_pf.tick()
            _print_drawables(drawables=game_pf.drawables(),
                             console=console)

            console.print(10, 10, str([e.name for e in game_pf.entities]))

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
                    # 3print(event)
                    if src.inputs.is_movement_key(event):# and player_entity.cooldown == 0:
                        delta = src.inputs.get_position_delta(event)
                        x, y = player_entity.position
                        new_x = x + delta.dx
                        new_y = y + delta.dy

                        # TODO: Add passability checking
                        if 0 < x < game_pf.width and 0 < y < game_pf.height:
                            player_entity.move_to(x=new_x, y=new_y)
                            print("{}, {} - Now at {}, {}".
                                  format(str(delta.dx),
                                         str(delta.dy),
                                         str(new_x),
                                         str(new_y)))
                    # elif event.sym == tcod.event.K_i:
                    #     test_menu(context=context)
                    else:
                        continue


if __name__ == "__main__":
    main()
