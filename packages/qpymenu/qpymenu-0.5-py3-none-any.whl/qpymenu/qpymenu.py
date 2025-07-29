# ============================================================
# pymenu.py v.5
# 
# A simple terminal menu system with ANSI formatting.
# Features:
#   - Nested menus and menu items
#   - ANSI color and formatting support
#   - Logs actions and displays them on the right side
#   - Supports threaded execution of menu item actions
#   - Prompts for arguments if "" is passed as args
#
# Usage:
#   Define menu items and submenus, then call menu.execute()
#
# Author: David J. Cartwright davidcartwright@hotmail.com
# Date: 2025-07-23
# ============================================================


import shutil
import threading
import ast

from .ansi import ansi

# ============================================================
# pyMenu class
#
# A class representing a terminal menu system with ANSI formatting.
#
# Features:
#   - Supports nested menus and menu items
#   - ANSI color and formatting for menu display
#   - Keeps a log of actions and displays them on the right side
#   - Allows threaded execution of menu item actions
#   - Prompts for arguments if "" is passed as args to a menu item
#
# Usage:
#   Create a pyMenu instance, add pyMenuItem or pyMenu (as submenus),
#   then call menu.execute() to start the menu loop.
#
# Methods:
#   - log_action(message): Add a message to the log
#   - draw(): Render the menu and log to the terminal
#   - execute(): Main menu loop for user interaction
#   - setformat(title_format, item_format): Set ANSI formatting for title/items
#   - additem(item): Add a pyMenuItem to the menu
#   - addsubmenu(submenu): Add a pyMenu as a submenu
#
# Date: 2025-07-23
# ============================================================
class pyMenu():
    def __init__(self, name: str = 'Main Menu'):
        self.name = name
        self.items = []
        self.title_format = ansi["fg_bright_blue"] + ansi["bold"]
        self.item_format = ansi["fg_bright_green"]
        self.parent = None
        self.log = []

    def log_action(self, message):
        self.log.append(message)
        if len(self.log) > 20:  # Keep last 20 logs
            self.log.pop(0)

    def draw(self):
        columns, rows = shutil.get_terminal_size(fallback=(80, 24))
        menu_width = columns // 2
        print(ansi['clear_screen'] + ansi['cursor_home'], end='')
        # Draw menu on left
        print(f"{self.title_format}{self.name}{ansi['reset']}")
        print("=" * len(self.name))
        for index, item in enumerate(self.items, start=1):
            print(f"{index}. {item.name} ({type(item).__name__})")
        if self.parent:
            print(f"{ansi['fg_bright_yellow']}0. Parent Menu: {self.parent.name}{ansi['reset']}")
        else:
            print(f"{ansi['fg_bright_yellow']}0. Exit{ansi['reset']}")
        # Draw log on right
        print(ansi['save_cursor'], end='')
        for i, log_entry in enumerate(self.log[-rows:]):
            print(f"\033[{i+1};{menu_width+2}H{ansi['fg_bright_cyan']}{log_entry}{ansi['reset']}")
        print(ansi['restore_cursor'], end='')

    def execute(self):
        current_menu = self
        while True:
            current_menu.draw()
            try:
                choice = int(input("Select an option: "))
                if choice == 0:
                    if current_menu.parent:
                        current_menu = current_menu.parent
                    else:
                        self.log_action("Exited menu.")
                        break
                elif 1 <= choice <= len(current_menu.items):
                    selected = current_menu.items[choice - 1]
                    if isinstance(selected, pyMenu):
                        current_menu = selected
                    else:
                        selected.execute()
                        self.log_action(f"Executed: {selected.name}")
                else:
                    self.log_action("Invalid selection.")
            except ValueError:
                self.log_action("Invalid input.")
    
    def setformat(self, title_format: str = ansi["fg_bright_blue"] + ansi["bold"],
                     item_format: str = ansi["fg_bright_green"]):
        self.title_format = title_format
        self.item_format = item_format
    
    def additem(self, item: 'pyMenuItem'):
        if isinstance(item, pyMenuItem):
            self.items.append(item)
        else:
            raise TypeError("Item must be an instance of pyMenuItem.")
        
    def addsubmenu(self, submenu: 'pyMenu'):
        submenu.parent = self
        self.items.append(submenu)



class pyMenuItem():
    def __init__(self, name: str, action: callable = None, wait=True, args=None, threaded=False):
        self.name = name
        self.action = action
        self.wait = wait
        self.args = args  # Default args or None
        self.threaded = threaded  # If True, run action in a separate thread

    def execute(self):
        if callable(self.action):
            args = self.args
            # Only prompt for arguments if args is exactly an empty string
            if args == "":
                arg_input = input(f"Enter arguments for {self.name} (comma-separated, or leave blank for none): ")
                if arg_input.strip():
                    try:
                        args = ast.literal_eval(f"({arg_input.strip()},)")
                    except Exception as e:
                        print(f"Error parsing arguments: {e}")
                        args = ()
                else:
                    args = ()
            elif args is None:
                args = ()
            # If args is a single value, make it a tuple
            if not isinstance(args, tuple):
                args = (args,)
            if self.threaded:
                t = threading.Thread(target=self.action, args=args)
                t.start()
                if self.wait:
                    t.join()
            else:
                self.action(*args)
            if self.wait and not self.threaded:
                print(ansi['bg_cyan'] + 'Press any key to return to menu' + ansi['reset'], end='')          
                input()
        else:
            print(f"Action for {self.name} is not callable.")




