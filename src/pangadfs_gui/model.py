# pangadfsgui/src/pangadfs_gui/model.py
# -*- coding: utf-8 -*-
# Copyright (C) 2021 Eric Truett
# Licensed under the MIT License

import pandas as pd

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, Signal, Slot


class PandasModel(QAbstractTableModel):
    """A model to interface a Qt view with pandas dataframe """

    dataframe_changed = Signal()

    def __init__(self, df: pd.DataFrame):
        super().__init__()
        self.df = df
        self.values = df.values
        self.dataframe_changed.connect(self.update_values)

    def rowCount(self, parent=QModelIndex()) -> int:
        """ Override method from QAbstractTableModel

        Return row count of the pandas DataFrame
        """
        if parent == QModelIndex():
            return len(self.df)

        return 0

    def columnCount(self, parent=QModelIndex()) -> int:
        """Override method from QAbstractTableModel

        Return column count of the pandas DataFrame
        """
        if parent == QModelIndex():
            return len(self.df.columns)
        return 0

    def data(self, index: QModelIndex, role=Qt.ItemDataRole) -> str:
        """Override method from QAbstractTableModel
        Return data cell from the pandas DataFrame
        Uses values accessor - is faster than iloc

        Args:
            index (QModelIndex): the index
            role (Qt.ItemDataRole): the role

        Returns:
            str

        """
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            return str(self.values[index.row(), index.column()])

        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole) -> str:
        """Override method from QAbstractTableModel
        Return dataframe index as vertical header data and columns as horizontal header data.

        Args:
            section (int): the section
            orientation (Qt.Orientatiton): the orientation
            role (Qt.ItemDataRole): the role

        Returns:
            str

        """
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self.df.columns[section])

            if orientation == Qt.Vertical:
                return str(self.df.index[section])

        return None

    def sort(self, col_number: int, order: Qt.SortOrder) -> None:
        """Sort table by given column number.

        Args:
            col_number (int): the column number
            order (Qt.SortOrder): Qt.DescendingOrder or Qt.AscendingOrder

        Returns:
            None

        """
        self.layoutAboutToBeChanged.emit()
        if order == Qt.DescendingOrder:
            ascending = False
        elif order == Qt.AscendingOrder:
            ascending = True
        self.df = self.df.sort_values(self.df.columns[col_number], ascending=ascending)
        self.dataframe_changed.emit()
        self.layoutChanged.emit()

    @Slot()
    def update_values(self) -> None:
        """Updates dataframe history"""
        self.values = self.df.values
