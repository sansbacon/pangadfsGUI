# pangadfsgui/src/pangadfs_gui/model.py
# -*- coding: utf-8 -*-
# Copyright (C) 2021 Eric Truett
# Licensed under the MIT License

from typing import Any, Union

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, Signal, Slot


try:
    import polars as pl
    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

if all((POLARS_AVAILABLE, PANDAS_AVAILABLE)):
    DfType = Union[pl.DataFrame, pd.DataFrame]
elif POLARS_AVAILABLE:
    DfType = pl.DataFrame
elif PANDAS_AVAILABLE:
    DfType = pd.DataFrame


class DataframeModel(QAbstractTableModel):
    """base implementation of a dataframe model"""

    dataframe_changed = Signal()

    def __init__(self, df: DfType, parent: Any = None):
        super().__init__(parent)
        self.df = df
        self.parent = parent

    def rowCount(self, parent=QModelIndex()) -> int:
        """ Override method from QAbstractTableModel

        Return row count of the pandas DataFrame
        """
        raise NotImplementedError

    def columnCount(self, parent=QModelIndex()) -> int:
        """Override method from QAbstractTableModel

        Return column count of the pandas DataFrame
        """
        raise NotImplementedError

    def data(self, index: QModelIndex, role=Qt.ItemDataRole):
        """Override method from QAbstractTableModel

        Return data cell from the pandas DataFrame
        """
        raise NotImplementedError

    def headerData(self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole):
        """Override method from QAbstractTableModel

        Return dataframe index as vertical header data and columns as horizontal header data.
        """
        raise NotImplementedError

    def loadCsv(self, fn):
        """Loads csv from file"""
        raise NotImplementedError

    def sort(self, Ncol, order):
        """Sort table by given column number.
        """
        raise NotImplementedError


class PandasModel(DataframeModel):

    def __init__(self, df: pd.DataFrame, parent: Any = None):
        super().__init__(df, parent)
        self.values = self.df.values
        self.dataframe_changed.connect(self.update_values)

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

    def loadCsv(self, fn, *args, **kwargs):
        """Loads csv from file"""
        self.df = pd.read_csv(fn, *args, **kwargs)
        self.dataframe_changed.emit()
        self.layoutChanged.emit()

    def rowCount(self, parent=QModelIndex()) -> int:
        """ Override method from QAbstractTableModel

        Return row count of the pandas DataFrame
        """
        if parent == QModelIndex():
            return len(self.df)

        return 0

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


class PolarsModel(DataframeModel):
    """A model to interface a Qt view with polars dataframe """

    def __init__(self, df: pl.DataFrame, parent=None):
        super().__init__(df, parent)
        self.df_index = list(range(self.df.height))

    def columnCount(self, parent=QModelIndex()) -> int:
        """Override method from DataframeModel

        Return column count of the polars DataFrame
        """
        if parent == QModelIndex():
            return self.df.width
        return 0

    def data(self, index: QModelIndex, role=Qt.ItemDataRole):
        """Override method from DataframeModel
        Return data cell from the polars DataFrame
        """
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            return str(self.df[index.row(), index.column()])
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole):
        """Override method from DataframeModel

        Return dataframe index as vertical header data and columns as horizontal header data.
        """
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self.df.columns[section])
            if orientation == Qt.Vertical:
                return str(self.df_index[section])
        return None

    def loadCsv(self, fn, *args, **kwargs):
        """Loads csv from file"""
        self.df = pl.read_csv(fn, *args, **kwargs)
        self.dataframe_changed.emit()
        self.layoutChanged.emit()

    def rowCount(self, parent=QModelIndex()) -> int:
        """ Override method from DataframeModel

        Return row count of the polars DataFrame
        """
        if parent == QModelIndex():
            return self.df.height
        return 0

    def sort(self, Ncol, order):
        """Sort table by given column number.
        """
        self.layoutAboutToBeChanged.emit()
        if order == Qt.DescendingOrder:
            reverse = True
        elif order == Qt.AscendingOrder:
            reverse = False
        self._dataframe = self.df.sort(self.df.columns[Ncol], reverse=reverse)
        self.dataframe_changed.emit()
        self.layoutChanged.emit()

    @Slot()
    def update_index(self) -> None:
        """Updates dataframe history"""
        self.df_index = list(range(self.df.height))