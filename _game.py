import tcod
import src
from typing import List, Dict, Type
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


def _draw_box(x_0: int, y_0: int,
              x_i: int, y_i: int,
              playfield: src.playfield.PlayField,
              fill_entity: Type[entities.MemoryBounds]):
    x_in_range: x_0 >= 0 and x_i < playfield.width
    y_in_range: y_0 >= 0 and y_i < playfield.width

    for x in range(x_0, x_i+1):
        for y in range(y_0, y_i+1):
            is_x_edge = (x == x_0) or (x == x_i)
            is_y_edge = (y == y_0) or (y == y_i)
            if is_x_edge or is_y_edge:
                cell = playfield.get_cell(x=x, y=y)
                entity = fill_entity()



def main() -> None:
    with tcod.context.new(width=WIDTH,
                          height=HEIGHT,
                          tileset=tileset,
                          title="Buffer Jack",
                          sdl_window_flags=FLAGS) as context:

        #TODO: Remove test contents and generate the main menu
        # game_pf = src.playfield.PlayField(width=floor(WIDTH/TILESET_SIZE),
        #                                   height=floor(HEIGHT/TILESET_SIZE),
        #                                   contents=((0, 0, entities.MemoryBounds()),
        #                                             (0, 1, entities.MemoryBounds()),
        #                                             (0, 2, entities.MemoryBounds()),
        #                                             (1, 0, entities.MemoryBounds()),
        #                                             (1, 2, entities.MemoryBounds()),
        #                                             (2, 0, entities.MemoryBounds()),
        #                                             (2, 2, entities.MemoryBounds()),
        #                                             (3, 0, entities.MemoryBounds()),
        #                                             (3, 2, entities.MemoryBounds()),
        #                                             (3, 1, entities.MemoryBounds()),
        #                                             (4, 0, entities.MemoryBounds()),
        #                                             (4, 1, entities.MemoryBounds()),
        #                                             (4, 1, entities.MemoryBounds()),
        #                                             (4, 2, entities.MemoryBounds())
        #                                             ))
        game_pf = src.playfield.PlayField(width=floor(WIDTH / TILESET_SIZE),
                                          height=floor(HEIGHT / TILESET_SIZE),
                                          contents=((0, 0, entities.MemoryBounds()),
                                                    (0, 1, entities.MemoryBounds())))

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

            # When a player entity's action cooldown reaches zero, wait for their input before continuing.
            if player_entity.cooldown == 0:
                has_acted: bool = False
                while not has_acted:
                    for event in tcod.event.get():
                        if event.type == "KEYDOWN":
                            # TODO: Expand this to include other gameplay keys
                            if src.inputs.is_movement_key(event) and player_entity.cooldown == 0:
                                # If the player wants to move, determine the direction and (if valid) execute it.
                                delta = src.inputs.get_position_delta(event)
                                x, y = player_entity.position

                                # Get new position and determine if in range
                                new_x = x + delta.dx
                                new_y = y + delta.dy

                                x_in_range = 0 <= new_x <= game_pf.width - 1
                                y_in_range = 0 <= new_y <= game_pf.height - 1

                                # TODO: Add passability checking
                                if x_in_range and y_in_range:
                                    # Execute the move only if the destination is also passable
                                    destination_passable: bool = game_pf.get_cell(x=new_x, y=new_y).passable
                                    if destination_passable:
                                        player_entity.move_to(x=new_x, y=new_y)
                                        has_acted = True

                            elif src.inputs.is_wait_action(event):
                                # If the player wants to wait, cool them down for 10 ticks.
                                player_entity.cooldown = 10

                        else:
                            continue

            for event in tcod.event.get():
                context.convert_event(event)
                console.print(5, 4, str(event))
                context.present(console)

                if event.type == "QUIT":
                    # Nuke it from the OS
                    raise SystemExit()

                if event.type == "WINDOWRESIZED":
                    pass

                if event.type == "KEYDOWN":
                    # TODO:
                    print(player_entity.cooldown)
                    if src.inputs.is_movement_key(event) and player_entity.cooldown == 0:
                        delta = src.inputs.get_position_delta(event)
                        x, y = player_entity.position
                        new_x = x + delta.dx
                        new_y = y + delta.dy

                        # TODO: Add passability checking
                        if (0 <= new_x <= game_pf.width - 1) and (0 <= new_y <= game_pf.height - 1):
                            player_entity.move_to(x=new_x, y=new_y)

                    # elif event.sym == tcod.event.K_i:
                    #     test_menu(context=context)
                    else:
                        continue


if __name__ == "__main__":
    main()
