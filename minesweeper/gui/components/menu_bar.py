""" The menu bar component for the minesweeper GUI. """
from PyQt5.QtWidgets import QMenuBar, QMenu, QActionGroup, QAction
from PyQt5.QtGui import QKeySequence


class MenuBar(QMenuBar):
    def __init__(self, parent):
        super().__init__(parent)

        game_menu = QMenu(self)
        game_menu.setTitle('&Game')
        new_action = QAction('&New', self)
        new_action.setShortcut(QKeySequence('F2'))
        new_action.setObjectName('new_menu_item')
        game_menu.addAction(new_action)
        game_menu.addSeparator()

        # Difficulty menu items.
        beginner = game_menu.addAction('Beginner')
        intermediate = game_menu.addAction('Intermediate')
        expert = game_menu.addAction('Expert')
        #custom = game_menu.addAction('Custom', self)
        beginner.setObjectName('beginner')
        intermediate.setObjectName('intermediate')
        expert.setObjectName('expert')
        #custom.setObjectName('custom')
        difficulty_group = QActionGroup(self)
        difficulty_group.addAction(beginner)
        difficulty_group.addAction(intermediate)
        difficulty_group.addAction(expert)
        #difficulty_group.addAction(custom)
        difficulty_group.setExclusive(True)
        # Make checkable and set a check mark in front of the selected difficulty.
        for item in difficulty_group.actions():
            item.setCheckable(True)
        expert.setChecked(True)
        #game_menu.addActions(difficulty_group.actions())

        game_menu.addSeparator()
        quit_action = QAction('Quit', self)
        quit_action.setObjectName('quit_menu_item')
        game_menu.addAction(quit_action)

        self.addMenu(game_menu)

        help_menu = QMenu(self)
        help_menu.setTitle('&Help')
        # self.addMenu(help_menu)
