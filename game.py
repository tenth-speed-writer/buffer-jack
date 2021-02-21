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
        while True:
            console = context.new_console(order="F")
            console.draw_frame(x=0, y=0,
                               width=console.width,
                               height=console.height,
                               title="BUFFER.JACK()")

            opt1 = MenuOption("Howdy!",
                              width=12,
                              height=5,
                              on_select=lambda x: print("Howdy!"),
                              subtext="It says howdy",
                              pad_horizontal=1,
                              pad_vertical=1,
                              color=(200, 255, 200))

            opt2 = MenuOption("Doody!",
                              width=12,
                              height=5,
                              on_select=lambda x: print("Doody!"),
                              subtext="It says doody",
                              pad_horizontal=1,
                              pad_vertical=1,
                              color=(200, 255, 200))

            print("Opt width, height: {},{}".format(str(opt1._width), str(opt1._height)))
            menu = Menu(30, 30)
            menu.add_option(opt1)
            menu.add_option(opt2)

            menu.add_option(MenuOption(text="Launch\nGame",
                                       width=console.width-16,
                                       height=5,
                                       on_select=lambda x: print("Player clicked the button!"),
                                       color=(130, 220, 130)))
            menu.open_menu(5, 5, console)

            # menu_renderable = menu.renderable()
            # for y in range(0, len(menu_renderable)):
            #     for x in range(0, len(menu_renderable[y])):
            #         char, color = menu_renderable[x][y]
            #         console.print(x+1, y+1, string=char, fg=color)

            context.present(console)




if __name__ == "__main__":
    main()