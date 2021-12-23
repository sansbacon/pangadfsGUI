# pangadfsgui/src/pangadfs_gui/view.py
# -*- coding: utf-8 -*-
# Copyright (C) 2021 Eric Truett
# Licensed under the MIT License

from pathlib import Path

import numpy as np
import pandas as pd

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (QTableView, QHBoxLayout, QHeaderView, QSizePolicy, QWidget, 
                               QVBoxLayout, QToolButton, QWidget, QStyle, QFileDialog)

from .model import PandasModel


class HorizontalHeader(QHeaderView):
    
    # https://stackoverflow.com/questions/69171881/qtableview-sortingenabled-and-column-selection
    def mousePressEvent(self, event):
        self.new_order = self.sortIndicatorOrder()
        super().mousePressEvent(event)
        height = self.height()
        x = event.position().x()
        logical_index = self.logicalIndexAt(x)
        x_left = self.sectionPosition(logical_index)
        x_right = x_left + self.sectionSize(logical_index)
        if (x_right - height) <= x <= x_right:
            self.new_order = (
                Qt.DescendingOrder
                if self.new_order == Qt.AscendingOrder
                else Qt.AscendingOrder
            )

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        x = event.position().x()
        logical_index = self.logicalIndexAt(x)
        self.setSortIndicator(logical_index, self.new_order)


class PandasWidget(QWidget):
    def __init__(self, df: pd.DataFrame = None):
        QWidget.__init__(self)

        # Getting the Model
        self.model = PandasModel(df if df is not None else pd.DataFrame())

        # Creating a QTableView
        self.table_view = QTableView()
        self.table_view.setModel(self.model)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSortingEnabled(True)

        # QTableView Headers
        # https://stackoverflow.com/questions/69171881/qtableview-sortingenabled-and-column-selection
        horizontal_header = HorizontalHeader(Qt.Horizontal)
        self.table_view.setHorizontalHeader(horizontal_header)
        horizontal_header.setSortIndicatorShown(True)
        horizontal_header.setSectionsClickable(True)
        self.table_view.setModel(self.model)
        horizontal_header.sortIndicatorChanged.connect(self.model.sort)
        horizontal_header.setSortIndicator(0, Qt.AscendingOrder)
        self.vertical_header = self.table_view.verticalHeader()
        self.vertical_header.setSectionResizeMode(QHeaderView.ResizeToContents)

        # QWidget Layout
        self.main_layout = QHBoxLayout()
        size = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        ## Left layout
        size.setHorizontalStretch(0)
        self.table_view.setSizePolicy(size)
        self.main_layout.addWidget(self.table_view)

        # Set the layout to the QWidget
        self.setLayout(self.main_layout)


class ProjectionsWidget(QWidget):
    """The projections widget"""
    def __init__(self):
        QWidget.__init__(self)
        self.current_df = None
        self.prev_df = None

        # tab 1: Projections
        self.main_layout = QVBoxLayout()
        
        # toolbars
        self.sub_layout = QHBoxLayout()
        self.sub_layout.setContentsMargins(0, 0, 0, 0)
        self.sub_layout.setAlignment(Qt.AlignLeft)

        # tool buttons
        self.butt1 = QToolButton()
        self.butt1.setToolTip('Open Projections File')
        self.butt1.clicked.connect(self.open_projections) 
        self.butt2 = QToolButton()
        self.butt2.setToolTip('Randomize Projections')
        self.butt2.clicked.connect(self.randomize_projections)                
        self.butt3 = QToolButton()
        self.butt3.setToolTip('Reset Projections')
        self.butt4 = QToolButton()
        self.butt4.setToolTip('Close Projections File')
        self.butt1.setIcon(QIcon(QPixmap(":/icons/openproj.png")))
        self.butt2.setIcon(QIcon(QPixmap(":/icons/shuffle.png")))
        self.butt3.setIcon(self.style().standardIcon(getattr(QStyle.StandardPixmap, 'SP_BrowserReload')))
        self.butt4.setIcon(self.style().standardIcon(getattr(QStyle.StandardPixmap, 'SP_FileDialogEnd')))
 
        self.sub_layout.addWidget(self.butt1)
        self.sub_layout.addWidget(self.butt2)
        self.sub_layout.addWidget(self.butt3)
        self.sub_layout.addWidget(self.butt4)
        self.icons_widget = QWidget()
        self.icons_widget.setLayout(self.sub_layout)
        self.main_layout.addWidget(self.icons_widget, 1)

        # pandas widget
        self.pandas_widget = PandasWidget()
        self.main_layout.addWidget(self.pandas_widget, 99)

        # add layout to widget
        self.setLayout(self.main_layout)

    def open_projections(self):
        """Opens projections file"""
        file_name, _ = QFileDialog.getOpenFileName(self, self.tr('Open File'), self.tr(str(Path.home())), '*')
        fpth = Path(file_name)
        if fpth.suffix == '.csv':
            if self.current_df is not None:
                self.prev_df = self.current_df.copy()
            self.current_df = pd.read_csv(fpth)
        elif fpth.suffix == '.excel':
            if self.current_df is not None:
                self.prev_df = self.current_df.copy()
            self.current_df = pd.read_excel(fpth)
        else:
            raise ValueError(f'Unsupported file format (csv and excel only): {fpth.suffix}')
        self.pandas_widget.table_view.setModel(PandasModel(self.current_df))
        self.update()

    def randomize_projections(self, projection_column=None):
        """randomizes projections"""
        self.prev_df = self.current_df.copy()
        if not projection_column:
            projection_column = self.current_df.columns[-1]
        random_weights = np.random.randint(low=-15, high=15, size=len(self.current_df)) / 100
        self.current_df[projection_column] = self.current_df[projection_column] + (self.current_df[projection_column] * random_weights).round(1)
        self.pandas_widget.table_view.setModel(PandasModel(self.current_df))
        self.update()