""" The menu bar component for the minesweeper GUI. """
from PyQt5.QtWidgets import QMenuBar, QMenu, QActionGroup, QAction
from PyQt5.QtGui import QKeySequence


class MenuBar(QMenuBar):
    def __init__(self, parent, debug_mode=False):
        """ :param debug_mode: Whether to add an extra debug menu. """
        super().__init__(parent)
        self.addMenu(self._create_game_menu())
        if debug_mode:
            self.addMenu(self._create_debug_menu())
        #help_menu = QMenu(self)
        #help_menu.setTitle('&Help')
        #self.addMenu(help_menu)

    def _create_game_menu(self):
        game_menu = QMenu(self)
        game_menu.setTitle('&Game')
        # New game action
        new_action = QAction('&New', self)
        new_action.setShortcut(QKeySequence('F2'))
        new_action.setObjectName('new_menu_item')
        game_menu.addAction(new_action)
        game_menu.addSeparator()
        # Difficulty group menu items.
        ## Create difficulty actions.
        beginner = game_menu.addAction('Beginner')
        intermediate = game_menu.addAction('Intermediate')
        expert = game_menu.addAction('Expert')
        #custom = game_menu.addAction('Custom', self)
        ## Name each of the actions.
        beginner.setObjectName('beginner')
        intermediate.setObjectName('intermediate')
        expert.setObjectName('expert')
        #custom.setObjectName('custom')
        ## Add each action to the group.
        difficulty_group = QActionGroup(self)
        difficulty_group.addAction(beginner)
        difficulty_group.addAction(intermediate)
        difficulty_group.addAction(expert)
        #difficulty_group.addAction(custom)
        # Make the group checkable and set a check mark in front of the selected difficulty.
        difficulty_group.setExclusive(True)
        for item in difficulty_group.actions():
            item.setCheckable(True)
        expert.setChecked(True)
        game_menu.addSeparator()
        # Quit action
        quit_action = QAction('Quit', self)
        quit_action.setObjectName('quit_menu_item')
        return game_menu

    def _create_debug_menu(self):
        debug_menu = QMenu(self)
        debug_menu.setTitle('&Debug')
        # Log state action.
        log_state = QAction('Log &state', self)
        log_state.setObjectName('log_state')
        debug_menu.addAction(log_state)
        # Log mines action.
        log_mines = QAction('Log &mines', self)
        log_mines.setObjectName('log_mines')
        debug_menu.addAction(log_mines)
        return debug_menu
