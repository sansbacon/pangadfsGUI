# pangadfsgui/src/pangadfs_gui/main.py
# -*- coding: utf-8 -*-
# Copyright (C) 2021 Eric Truett
# Licensed under the MIT License

from pathlib import Path

import pandas as pd

from PySide6.QtWidgets import (QMainWindow, QHBoxLayout, QVBoxLayout, QToolButton, QTreeWidget, QWidget, QFileDialog, QTabWidget, QStyle)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence, QIcon, QPixmap

from .model import PandasModel
from .view import PandasWidget
from .resources import *


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
        t1_layout = QVBoxLayout()
        
        # toolbars
        t1_1_layout = QHBoxLayout()
        t1_1_layout.setContentsMargins(0, 0, 0, 0)
        t1_1_layout.setAlignment(Qt.AlignLeft)

        # tool buttons
        butt1 = QToolButton()
        butt1.setToolTip('Open Projections File')
        butt2 = QToolButton()
        butt2.setToolTip('Randomize Projections')
        butt3 = QToolButton()
        butt3.setToolTip('Reset Projections')
        butt4 = QToolButton()
        butt4.setToolTip('Close Projections File')

        #QIcon(QPixmap(":/icons/openproj.png"))
        #QIcon(QPixmap(":/icons/shuffle.png"))
        #b1_pixmapi = getattr(QStyle.StandardPixmap, 'SP_FileDialogStart')
        b1_icon = QIcon(QPixmap(":/icons/openproj.png")) #self.style().standardIcon(b1_pixmapi)
        butt1.setIcon(b1_icon)
        #b2_pixmapi = getattr(QStyle.StandardPixmap, 'SP_ComputerIcon')
        b2_icon = QIcon(QPixmap(":/icons/shuffle.png")) #self.style().standardIcon(b2_pixmapi)
        butt2.setIcon(b2_icon)
        butt3.setIcon(self.style().standardIcon(getattr(QStyle.StandardPixmap, 'SP_BrowserReload')))
        butt4.setIcon(self.style().standardIcon(getattr(QStyle.StandardPixmap, 'SP_FileDialogEnd')))
 
        t1_1_layout.addWidget(butt1)
        t1_1_layout.addWidget(butt2)
        t1_1_layout.addWidget(butt3)
        t1_1_layout.addWidget(butt4)
        t1_1_widget = QWidget()
        t1_1_widget.setLayout(t1_1_layout)
        t1_layout.addWidget(t1_1_widget, 1)

        # pandas widget
        self.projections_widget = PandasWidget()
        t1_layout.addWidget(self.projections_widget, 99)

        # wrapper widget for the tab
        t1_widget = QWidget()
        t1_widget.setLayout(t1_layout)
        self.tabs.addTab(t1_widget, "Projections")

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
        # Open Action
        file_open_action = QAction(QIcon('open.png'), '&Open Projections', self)    
        file_open_action.setShortcut("Ctrl+O")
        file_open_action.setStatusTip('Open projections file')
        file_open_action.triggered.connect(self.file_open)

        # Exit QAction
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)

        # add to file menu
        self.file_menu.addAction(file_open_action)
        self.file_menu.addAction(exit_action)

    def file_open(self):
        file_name, _ = QFileDialog.getOpenFileName(self, self.tr('Open File'), self.tr(str(Path.home())), '*')
        fpth = Path(file_name)
        if fpth.suffix == '.csv':
            df = pd.read_csv(fpth)
        elif fpth.suffix == '.excel':
            df = pd.read_excel(fpth)
        else:
            raise ValueError(f'Unsupported file format (csv and excel only): {fpth.suffix}')
        self.projections_widget.table_view.setModel(PandasModel(df))
        self.update()
        self.status.showMessage("Data loaded.")
