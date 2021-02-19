# PopupMenu
# Version: v1.2.1
# Description: A low-fuss, infinitely nested popup menu for pygame.
# Author: Gummbum
# Home: http://code.google.com/p/simple-pygame-menu/
# Source: See home.


import pygame
from pygame import Rect, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION, USEREVENT
from UI.TradeUI import TradeUI
from config import HUDConf
from config.UIConf import *


class PopupMenu(object):
    """popup_menu.PopupMenu
    PopupMenu(data, block=True) : return menu

    data -> list; the list of strings and nested lists.
    pos -> tuple; the xy screen coordinate for the topleft of the main menu; if
        None, the mouse position is used.
    block -> boolean; when True popup_menu will run its own event loop, blocking
        your main loop until it exits; when False popup_menu.get_events() will
        intercept events it cares about and return unhandled events to the
        caller.

    Note: For a non-blocking menu, use the NonBlockingPopupMenu instead. This
    class supports non-blocking, but it is more cumbersome to use than the
    NonBlockingPopupMenu class.

    The first string in the data list is taken as the menu title. The remaining
    strings are menu items. A nested list becomes a submenu. Submenu lists must
    also contain strings for menu title and menu items. Submenus can be
    theoretically infinitely nested.

    The menu runs a mini event loop. This will block the caller until it exits.
    Upon exiting, the screen is restored to its prior state.

    Left-clicking outside the topmost menu will quit the entire menu. Right-
    clicking anywhere will close the topmost submenu; if only the main menu
    remains the menu will exit. Left-clicking a menu item in the topmost menu
    will post a USEREVENT for the caller to process.

    The USEREVENT will have attributes: code='MENU', name=popup_menu.name,
    item_id=menu_item.item_id, text=menu_item.text. name is first element in a
    menu data list. item_id corresponds to the Nth element in a menu data list,
    incremented from 0; submenu items count as one menu_id even though they are
    never posted in an event. text is the string value of the Nth element in the
    menu data list. Thus, combinations of name and menu_id or name and text can
    be used to uniquely identify menu selections.

    Example menu data and resulting event data:

        ['Main',            # main menu title
         'Item 0',          # name='Main', menu_id=0, text='Item 0'
            ['Submenu',     # submenu title
             'Item 0',      # name='Submenu', menu_id=0, text='Item 0'
             'Item 1',      # name='Submenu', menu_id=0, text='Item 1'
            ],
         'Item 2',          # name='Main', menu_id=2, text='Item 2'
        ]

    High-level steps for a blocking menu:

    1.  Fashion a nested list of strings for the PopupMenu constructor.
    2.  Upon creation, the menu runs its own loop.
    3.  Upon exit, control is returned to the caller.
    4.  Handle the resulting USEREVENT event in the caller where
        event.name=='your menu title', event.item_id holds the selected item
        number, and event.text holds the item label.

    High-level steps for a non-blocking menu:

    Note: This usage exists to support the NonBlockingPopupMenu class and
    custom non-blocking implementations; for typical use NonBlockingPopupMenu
    is recommended.

    1.  Fashion a nested list of strings for the PopupMenu constructor.
    2.  Store the menu object in a variable.
    3.  Devise a means for the main loop to choose whether to draw the menu and pass
        it events.
    4.  Call menu.draw() to draw the menu.
    5.  Pass pygame events to menu.handle_event() and process the unhandled events
        that are returned as you would pygame's events.
    6.  Upon menu exit, one or two USEREVENTs are posted via pygame. Retrieve
        them and recognize they are menu events (event.code=='MENU').
        a.  The menu-exit event signals the main loop it has exited, with or
            without a menu selection. Recognize this by event.name==None. Upon
            receiving this event the main loop should stop using the menu's
            draw() and get_events() (until the next time it wants to post the
            menu to the user).
        b.  The menu-selection event signals the main loop that a menu item was
            selected. Recognize this by event.name=='your menu title'.
            event.menu_id holds the selected item number, and event.text holds
            the item label.
    7.  Destroying the menu is not necessary. But creating and destroying it may
        be a convenient means to manage the menu state (i.e. to post it or not).
    """

    def __init__(self, data, pos=None, block=True):
        # list of open Menu() objects
        self.menus = []
        # key to main menu data
        self.top = data[0]
        # dict of menus, keyed by menu title
        self.data = {self.top: []}
        # walk the nested list, creating the data dict for easy lookup
        self._walk(self.top, list(data))

        # make the main menu
        self._make_menu(self.data[self.top], pos)

        # Save the display surface; use to clear screen
        self.screen = pygame.display.get_surface()
        self.clear_screen = self.screen.copy()

        if block:
            self._run(block)

    def handle_event(self, e, block=False):
        unhandled = None
        if e.type == MOUSEBUTTONUP:
            if e.button == 1:
                menu = self.menus[-1]
                item = menu.menu_item
                if item:
                    if isinstance(item.text, SubmenuLabel):
                        # open submenu
                        key = item.text[:-3]
                        self._make_menu(self.data[key])
                    else:
                        # pick item (post event)
                        pygame.event.post(self._pick_event(menu, item))
                        self._quit(block)
                        return self._quit_event()
                else:
                    # close menu
                    self._quit(block)
                    return self._quit_event()
            elif e.button == 3:
                # close menu
                if len(self.menus) == 1:
                    self._quit(block)
                    return self._quit_event()
                else:
                    self._del_menu()
        elif e.type == MOUSEMOTION:
            self.mouse_pos = e.pos
            self.menus[-1].check_collision(self.mouse_pos)
            unhandled = e
        elif e.type == MOUSEBUTTONDOWN:
            pass
        else:
            unhandled = e
        return unhandled

    def draw(self):
        for menu in self.menus:
            menu.draw()

    def _pick_event(self, menu, item):
        event = pygame.event.Event(
            USEREVENT, code="MENU", name=menu.name, item_id=item.item_id, text=item.text
        )
        return event

    def _quit_event(self):
        event = pygame.event.Event(
            USEREVENT, code="MENU", name=None, item_id=-1, text="_MENU_EXIT_"
        )
        return event

    def _run(self, block=True):
        screen = self.screen
        clock = pygame.time.Clock()
        self.mouse_pos = pygame.mouse.get_pos()
        self.running = True
        while self.running:
            self.screen.blit(self.clear_screen, (0, 0))
            self.draw()
            pygame.display.flip()
            self.handle_event(pygame.event.get())
            clock.tick(60)

    def _walk(self, key, data):
        # Recursively walk the nested data lists, building the data dict for
        # easy lookup.
        for i, ent in enumerate(data):
            if isinstance(ent, str):
                self.data[key].append(ent)
            else:
                ent = list(ent)
                new_key = ent[0]
                ent[0] = SubmenuLabel(new_key)
                self.data[key].append(ent[0])
                self.data[new_key] = []
                self._walk(new_key, list(ent))

    def _make_menu(self, data, pos=None):
        # Make a menu from data list and add it to the menu stack.
        if self.menus:
            # position submenu relative to parent
            parent = self.menus[-1]
            rect = parent.menu_item.rect
            pos = rect.right, rect.top
            # unset the parent's menu_item (for appearance)
            parent.menu_item = None
        else:
            # position main menu at mouse
            if pos is None:
                pos = pygame.mouse.get_pos()
        name = data[0]
        items = data[1:]
        self.menus.append(Menu(pos, name, items, self.Game))

    def _del_menu(self):
        # Remove the topmost menu from the menu stack.
        self.menus.pop()

    def _quit(self, block):
        # Put the original screen contents back.
        if block:
            self.screen.blit(self.clear_screen, (0, 0))
            pygame.display.flip()
        self.running = False


class NonBlockingPopupMenu(PopupMenu):
    """popup_menu.NonBlockingPopupMenu
    NonBlockingPopupMenu(data, pos=None, show=False) : return menu

    data -> list; the list of strings and nested lists.
    pos -> tuple; the xy screen coordinate for the topleft of the main menu; if
        None, the mouse position is used.
    show -> boolean; make the menu visible in the constructor.

    visible is a read-write property that sets and gets the boolean value
    representing the state. The show() and hide() methods are equivalent
    alternatives to using the property.

    Note that the constructor does not copy the data argument. Changes to the
    contents will result in changes to the menus once show() is called or
    visible is set to True. In addition, data can be entirely replaced by
    setting menu.init_data.

    High-level steps for a non-blocking menu:

    1.  Fashion a nested list of strings for the NonBlockingPopupMenu constructor.
    2.  Store the menu object in a variable.
    3.  Construct the NonBlockingPopupMenu object.
    4.  Detect the condition that triggers the menu to post, and call menu.show()
        (or set menu.visible=True).
    5.  Call menu.draw() to draw the menu. If it is visible, it will be drawn.
    6.  Pass pygame events to menu.handle_event() and process the unhandled events
        that are returned as you would pygame's events. If the menu is not visible
        the method will immediately return the list passed in, unchanged.
    7.  Upon menu exit, one or two USEREVENTs are posted via pygame. Retrieve them
        and recognize they are menu events (i.e., event.code=='MENU').
        a.  A menu-exit event signals the menu has detected an exit condition, which
            may or many not be accompanied by a menu selection. Recognize this by
            event.name==None or event.menu_id==-1. Upon receiving this event the
            main loop should call menu.hide() (or set menu.visible=False).
        b.  A menu-selection event signals the main loop that a menu item was
            selected. Recognize this by event.name=='your menu title'. event.menu_id
            holds the selected item number, and event.text holds the item label.
    8.  Destroying the menu is optional.
    9.  Assigning to menu.init_data, or changing its contents or that of the
        original list variable, will result in a modified menu the next time
        menu.show() is called (or menu.visible is set to True)."""

    def __init__(self, data, gameController, pos=None, show=False):
        self.init_data = data
        self._init_pos = pos
        self.Game = gameController

        if show:
            self.show()
        else:
            self.hide()

    def bind(self, Hero, TargetHero):

        self.Hero = Hero
        self.Target = TargetHero

    def show(self):
        """generate the menu geometry and graphics, and makes the menu visible"""
        super(NonBlockingPopupMenu, self).__init__(
            self.init_data, pos=self._init_pos, block=False
        )
        self._show = True

    def hide(self):
        """destroy the menu geometry and grpahics, and hides the menu"""
        if hasattr(self, "menus"):
            del self.menus[:]
        self._show = False

    @property
    def visible(self):
        return self._show

    @visible.setter
    def visible(self, val):
        if val:
            self.show()
        else:
            self.hide()

    def handle_event(self, event):
        """preemptively return if the menu is not visible; else, call the
        superclass's method.
        """
        if self._show:
            return super(NonBlockingPopupMenu, self).handle_event(event)
        else:
            return event

    def draw(self):
        """preemptively return if the menu is not visible; else, call the
        superclass's method.
        """
        if self._show:
            super(NonBlockingPopupMenu, self).draw()

    def checkEvents(self, e):
        e = self.handle_event(e)
        if e != None and e.type == USEREVENT:
            if e.code == "MENU":
                if e.name is None:
                    self.hide()
                elif e.name == "Character Options":
                    if e.text == "Inventory":
                        if self.Target.Inventory._show:
                            self.Target.Inventory.close()
                        else:
                            self.Target.Inventory.open = True
                    elif e.text == "Spellbook":
                        if self.Target.SpellBook._show:
                            self.Target.SpellBook.transitionFlag = "close"
                        else:
                            self.Target.SpellBook.open = True
                    elif e.text == "Trade":
                        TradeUI(self.Game, self.Hero, self.Target).show()
                    elif e.text == "Fight":
                        self.Hero.createFight([self.Hero, self.Target])


class SubmenuLabel(str):
    """popup_menu.SubmenuLabel
    SubmenuLabel(s) : return label

    s -> str; the label text

    This is a helper class for strong-typing of submenu labels.

    This class is not intended to be used directly. See PopupMenu or
    NonBlockingPopupMenu.
    """

    def __new__(cls, s):
        return str.__new__(cls, s + "...")


class MenuItem(object):
    """popup_menu.MenuItem
    MenuItem(text, item_id) : return menu_item

    text -> str; the display text.
    item_id -> int; the numeric ID; also the item_id attribute returned in the
        pygame event.

    This class is not intended to be used directly. Use PopupMenu or
    NonBlockingPopupMenu instead, unless designing your own subclass.
    """

    def __init__(self, text, item_id):
        self.text = text
        self.item_id = item_id
        self.image = pygame.font.Font(DUNGEON_FONT, 20).render(text, True, text_color)
        self.rect = self.image.get_rect()


class Menu(object):
    """popup_menu.Menu
    Menu(pos, name, items) : return menu

    pos -> (x,y); topleft coordinates of the menu.
    name -> str; the name of the menu.
    items -> list; a list containing strings for menu items labels.

    This class is not intended to be used directly. Use PopupMenu or
    NonBlockingPopupMenu instead, unless designing your own subclass.
    """

    def __init__(self, pos, name, items, gameController):

        self.Game = gameController
        screen = pygame.display.get_surface()
        screen_rect = screen.get_rect()
        self.name = name
        self.items = []
        self.menu_item = None
        # Make the frame rect
        x, y = pos
        self.rect = Rect(x, y, 0, 0)
        self.rect.width += margin * 2
        self.rect.height += margin * 2
        # Make the title image and rect, and grow the frame rect
        TitleFont = pygame.font.SysFont(None, 20)
        TitleFont.bold = True
        self.title_image = TitleFont.render(name, True, text_color)
        self.title_rect = self.title_image.get_rect(topleft=(x + margin, y + margin))
        self.rect.width = margin * 2 + self.title_rect.width
        self.rect.height = margin + self.title_rect.height
        # Make the item highlight rect
        self.hi_rect = Rect(0, 0, 0, 0)

        # Make menu items
        n = 0
        for item in items:
            menu_item = MenuItem(item, n)
            self.items.append(menu_item)
            self.rect.width = max(self.rect.width, menu_item.rect.width + margin * 2)
            self.rect.height += menu_item.rect.height + margin
            n += 1
        self.rect.height += margin

        # Position menu fully within view
        if not screen_rect.contains(self.rect):
            savex, savey = self.rect.topleft
            self.rect.clamp_ip(screen_rect)
            self.title_rect.top = self.rect.top + margin
            self.title_rect.left = self.rect.left + margin

        # Position menu items within menu frame
        y = self.title_rect.bottom + margin
        for item in self.items:
            item.rect.x = self.rect.x + margin
            item.rect.y = y
            y = item.rect.bottom + margin
            item.rect.width = self.rect.width - margin * 2

        # Calculate highlight rect's left-alignment and size
        self.hi_rect.left = menu_item.rect.left
        self.hi_rect.width = self.rect.width - margin * 2
        self.hi_rect.height = menu_item.rect.height

        # Create the menu frame and highlight frame images
        self.bg_image = pygame.transform.scale(HUDConf.PLAYER_ICON_SLOT, self.rect.size)
        self.hi_image = pygame.surface.Surface(self.hi_rect.size)
        # self.bg_image.fill(bg_color)
        self.hi_image.fill(hi_color)
        # Draw menu border
        rect = self.bg_image.get_rect()
        # pygame.draw.rect(self.bg_image, glint_color, rect, 1)
        t, l, b, r = rect.top, rect.left, rect.bottom, rect.right
        # pygame.draw.line(self.bg_image, shadow_color, (l, b - 1), (r, b - 1), 1)
        # pygame.draw.line(self.bg_image, shadow_color, (r - 1, t), (r - 1, b), 1)
        # Draw title divider in menu frame
        left = margin
        right = self.rect.width - margin * 2
        y = self.title_rect.height + 1
        # pygame.draw.line(self.bg_image, shadow_color, (left, y), (right, y))

    def draw(self):
        # Draw the menu on the main display.

        self.Game.screen.blit(self.bg_image, self.rect)
        self.Game.screen.blit(self.title_image, self.title_rect)
        for item in self.items:
            if item is self.menu_item:
                self.hi_rect.top = item.rect.top
                self.Game.screen.blit(self.hi_image, self.hi_rect)
            self.Game.screen.blit(item.image, item.rect)

    def check_collision(self, mouse_pos):
        # Set self.menu_item if the mouse is hovering over one.
        self.menu_item = None
        if self.rect.collidepoint(mouse_pos):
            for item in self.items:
                if item.rect.collidepoint(mouse_pos):
                    self.menu_item = item
                    break
