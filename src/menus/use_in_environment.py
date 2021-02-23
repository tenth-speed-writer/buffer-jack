import tcod
from typing import List, Tuple, Callable
from src.inputs.position_delta import PositionDelta
from .menu import Menu, MenuOption


class UseInEnvironmentMenuHandler(tcod.event.EventDispatch):
    def __init__(self, menu, menus:List[Menu]):

        super().__init__()
        self._menu = menu

    def cmd_close_menu(self):
        """Set its .is_open to False, breaking the menu loop."""
        self._menu.close()

    def ev_keydown(self, event: tcod.event.KeyDown):
        up_keys = [tcod.event.K_UP, tcod.event.K_KP_8, tcod.event.K_KP_PLUS]
        down_keys = [tcod.event.K_DOWN, tcod.event.K_KP_2, tcod.event.K_KP_MINUS]
        select_keys = [tcod.event.K_SPACE,
                       tcod.event.K_RETURN,
                       tcod.event.K_RETURN2,
                       tcod.event.K_KP_ENTER]
        exit_keys = [tcod.event.K_ESCAPE]

        # TODO: Add page up/page down for multi-entity skips
        if event.sym in up_keys:
            self._menu.change_selection(PositionDelta(dx=0, dy=-1))
        elif event.sym in down_keys:
            self._menu.change_selection(PositionDelta(dx=0, dy=1))
        elif event.sym in select_keys:
            opt: MenuOption = self._menu.contents[self._menu.selected]
            opt.on_select(None)
        elif event.sym in exit_keys:
            # TODO: Tell the menu to close
            self.cmd_close_menu()

    def ev_quit(self, event: tcod.event.Quit):
        SystemExit()


class UseInEnvironmentMenu(Menu):
    """The menu displayed when the player wants to Use a cell in the environment, but there's more than one usable."""
    def __init__(self,options: List[Tuple[str, Callable]],
                 console: tcod.console.Console,
                 width: int = 50,
                 height: int = 30):

        # Determine how much of the console we're
        if height > console.height or width > console.width:
            raise ValueError("Height and width must be no greater than that of the console. Got {}, {}"
                             .format(str(width), str(height)))

        contents = [MenuOption(height=2,
                               width=width-2,
                               text=name,
                               on_select=on_select)
                    for name, on_select in options]

        super().__init__(width=width,
                         height=height,
                         spacing=1,
                         contents=contents,
                         padding=(2, 2, 2, 2),
                         has_border=True)

