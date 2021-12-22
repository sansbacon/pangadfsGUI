# pangadfsgui/src/pangadfs_gui/view.py
# -*- coding: utf-8 -*-
# Copyright (C) 2021 Eric Truett
# Licensed under the MIT License


import pandas as pd

from PySide6.QtWidgets import QTableView, QHBoxLayout, QHeaderView, QSizePolicy, QWidget
from PySide6.QtCore import Qt

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

        #self.horizontal_header = self.table_view.horizontalHeader()
        #self.horizontal_header.setSectionResizeMode(
        #                       QHeaderView.ResizeToContents
        #                     )
        #self.horizontal_header.setStretchLastSection(True)

        self.vertical_header = self.table_view.verticalHeader()
        self.vertical_header.setSectionResizeMode(
                             QHeaderView.ResizeToContents
                             )

        # QWidget Layout
        self.main_layout = QHBoxLayout()
        size = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        ## Left layout
        size.setHorizontalStretch(0)
        self.table_view.setSizePolicy(size)
        self.main_layout.addWidget(self.table_view)

        # Set the layout to the QWidget
        self.setLayout(self.main_layout)

