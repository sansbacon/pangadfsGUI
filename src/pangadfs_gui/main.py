# pangadfsgui/src/pangadfs_gui/main.py
# -*- coding: utf-8 -*-
# Copyright (C) 2021 Eric Truett
# Licensed under the MIT License

from pathlib import Path

import pandas as pd

from PySide6.QtWidgets import (QMainWindow, QHBoxLayout, QVBoxLayout, QToolButton, QTreeWidget, QWidget, QFileDialog, QTabWidget, QStyle)
from PySide6.QtCore import Qt, QRunnable, Slot, QThreadPool
from PySide6.QtGui import QAction, QKeySequence, QIcon, QPixmap

from pangadfs_gui.model import PandasModel
from pangadfs_gui.widget import PandasWidget, ProjectionsWidget
from pangadfs_gui.resources import *


class OptimizerWorker(QRunnable):
    '''Worker thread for optimizer'''

    @Slot()
    def run(self):
        '''
        Your code goes in this function
        '''
        print("Thread start")

        print("Thread complete")


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

        # create tree view
        self.tree = QTreeWidget()

        # create tabbed interface
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setDocumentMode(True)

        # tab 1: Projections
        self.projections_widget = ProjectionsWidget()
        self.tabs.addTab(self.projections_widget, "Projections")

        # tab 2: Summary
        self.tabs.addTab(PandasWidget(), "Summary")

        # tab 3: Lineups
        self.tabs.addTab(PandasWidget(), "Lineups")

        # now add 2-panel layout
        layout = QHBoxLayout()
        layout.addWidget(self.tree, 20)
        layout.addWidget(self.tabs, 80)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        
    def create_menus(self):
        """Creates menus"""
        # Menu Items
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("&File")
        self.edit_menu = self.menu.addMenu("&Edit")
        self.help_menu = self.menu.addMenu("&Help")
        
        ## FILE MENU

        # Exit QAction
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)

        # add to file menu
        self.file_menu.addAction(exit_action)