# pangadfsgui/src/pangadfs_gui/main.py
# -*- coding: utf-8 -*-
# Copyright (C) 2021 Eric Truett
# Licensed under the MIT License

import webbrowser

from PySide6.QtCore import QUrl
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QMainWindow, QTabWidget

from pangadfs_gui.model import *
from pangadfs_gui.widget import *
from pangadfs_gui.resources import *


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("pangadfs GUI")

        # set statusbar / menus
        self.status = self.statusBar()
        self.create_menus()

        # Window dimensions
        geometry = self.screen().availableGeometry()
        self.setMinimumSize(geometry.width() * 0.8, geometry.height() * 0.6)

        # create tabbed interface
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setDocumentMode(True)

        # tab 1: Projections
        self.tabs.addTab(TabWidget(config=ConfigManager()), "Projections")

        # tab 2: Summary
        self.tabs.addTab(TabWidget(config=ConfigManager()), "Summary")

        # tab 3: Lineups
        self.tabs.addTab(TabWidget(config=ConfigManager()), "Lineups")

        self.setCentralWidget(self.tabs)
        
    def create_menus(self):
        """Creates menus"""
        # Menu Items
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("&File")
        self.edit_menu = self.menu.addMenu("&Edit")
        self.edit_menu = self.menu.addMenu("&View")
        self.edit_menu = self.menu.addMenu("&Tools")
        self.help_menu = self.menu.addMenu("&Help")
        
        ## FILE MENU

        # Exit QAction
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)

        # add to file menu
        self.file_menu.addAction(exit_action)

        ## HELP MENU

        # Exit QAction
        help_action = QAction("View Online Help", self)
        help_action.triggered.connect(self.view_help)

        # add to file menu
        self.help_menu.addAction(help_action)

    def view_help(self):
        """Opens online help"""
        url = 'https://www.github.com/sansbacon/pangadfsgui'
        webbrowser.open_new(url)