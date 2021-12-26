# pangadfsgui/src/pangadfs_gui/view.py
# -*- coding: utf-8 -*-
# Copyright (C) 2021 Eric Truett
# Licensed under the MIT License

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableView, QHeaderView, QWidget

from pangadfs_gui.model import DataframeModel


class HorizontalHeader(QHeaderView):
    """This enables click to sort on table widget"""
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


class DataframeView(QTableView):
    """Base dataframe view"""
    
    def __init__(self, model: DataframeModel):
        # Creating a QTableView
        super().__init__()
        self.model = model
        self.view = QTableView()
        self.view.setModel(self.model)
        self.view.setAlternatingRowColors(True)
        self.view.setSortingEnabled(True)

        # QTableView Headers
        # https://stackoverflow.com/questions/69171881/qtableview-sortingenabled-and-column-selection
        horizontal_header = HorizontalHeader(Qt.Horizontal)
        self.view.setHorizontalHeader(horizontal_header)
        horizontal_header.setSortIndicatorShown(True)
        horizontal_header.setSectionsClickable(True)
        horizontal_header.sortIndicatorChanged.connect(self.model.sort)
        horizontal_header.setSortIndicator(0, Qt.AscendingOrder)
        self.vertical_header = self.view.verticalHeader()
        self.vertical_header.setSectionResizeMode(QHeaderView.ResizeToContents)