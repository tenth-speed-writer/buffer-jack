import tcod
from src.menus import Menu, MenuOption
from src.inputs.gameplay import GameplayHandler
from src.playfield import PlayField
from src.entity.entities import Mobile
from src.sigil import Sigil
from typing import List, Tuple, Optional, Dict

# Default window resolution
WIDTH, HEIGHT = 720, 480
TILESET_SIZE = 16
FLAGS = tcod.context.SDL_WINDOW_RESIZABLE | tcod.context.SDL_WINDOW_MAXIMIZED


def main():
    """Launch the main game loop."""
    # On launch, open the main menu.
    tileset = tcod.tileset.load_tilesheet("tilesets/yayo_c64_16x16.png", 16, 16,
                                          charmap=tcod.tileset.CHARMAP_CP437)

    # Create a new window/SDL context
    with tcod.context.new(width=WIDTH,
                          height=HEIGHT,
                          sdl_window_flags=FLAGS,
                          tileset=tileset) as context:
        # Render the main menu
        # TODO: Make the main menu its own class
        console = context.new_console(order="F")
        main_menu = Menu(width=console.width - 2,  # -2 to account for the border we've already drawn
                         height=console.height - 2)

        main_menu.add_option(MenuOption(text="Launch\nGame",
                                        width=min(console.width - 6, 14),  # Ideally 14, but shrink to fit if needed.
                                        height=5,
                                        on_select=lambda: print("Player clicked the button!"),
                                        color=(130, 220, 130)))
        menus: Optional[List[Tuple[int, int, Menu]]] = None  # [(1, 1, main_menu)]

        # The variable which will hold the active playfield

        player_char = Mobile(size=4,
                             sigil=Sigil("@"),
                             name="Player Character")
        playfield: Optional[PlayField] = PlayField(40, 40)
        player_char.introduce_at(10, 10, playfield)
        playfield.dispatch = GameplayHandler(playfield, player_char)

        while True:
            # Create the console and draw
            console = context.new_console(order="F", min_columns=32, min_rows=24)
            console.draw_frame(x=0, y=0,
                               width=console.width,
                               height=console.height,
                               title="BUFFER.JACK()")

            # Render the playfield, if one is open
            if playfield:
                playfield.tick()
                pf_rows: List[Dict] = playfield.drawables()
                for r in pf_rows:
                    console.print(x=r["x"],
                                  y=r["y"],
                                  string=r["character"],
                                  fg=r["rgb"])

            if menus:
                # Render each menu that's currently open
                for _x, _y, _menu in menus:
                    _menu.render_menu(_x, _y, console)
                top_menu = menus[-1][2]  # The topmost menu will be third element of the last tuple in the list
                dispatcher: tcod.event.EventDispatch = top_menu.dispatch

                # Hand event control to the last
                for event in tcod.event.get():
                    dispatcher.dispatch(event)
            else:
                # If no menu is open, but the playfield is, then use its event handler
                dispatcher: tcod.event.EventDispatch = playfield.dispatch

            context.present(console)
            for event in tcod.event.get():
                context.convert_event(event)  # Converting the event fills in mouse event tile coordinates
                dispatcher.dispatch(event)



        # HANDLING MENUS:
        # Draw each menu on top of one another for each menu in a menus variable,
        # then pass control of the handler to that menu's handler





if __name__ == "__main__":
    main()