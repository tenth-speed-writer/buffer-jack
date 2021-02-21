import tcod
from math import floor
from src.menus import Menu, MenuOption

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
        console = context.new_console(order="F")
        menu = Menu(width=console.width - 2,  # -2 to account for the border we've already drawn
                    height=console.height - 2)

        menu.add_option(MenuOption(text="Launch\nGame",
                                   width=min(console.width - 6, 14),  # Ideally 14, but shrink to fit if needed.
                                   height=5,
                                   on_select=lambda x: print("Player clicked the button!"),
                                   color=(130, 220, 130)))
        menu.open_menu(1, 1, console, context)
        while True:
            console = context.new_console(order="F")
            console.draw_frame(x=0, y=0,
                               width=console.width,
                               height=console.height,
                               title="BUFFER.JACK()")

        # HANDLING MENUS:
        # Draw each menu on top of one another for each menu in a menus variable,
        # then pass control of the handler to that menu's handler





if __name__ == "__main__":
    main()