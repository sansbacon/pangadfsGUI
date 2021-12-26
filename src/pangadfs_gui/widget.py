# pangadfsgui/src/pangadfs_gui/widget.py
# -*- coding: utf-8 -*-
# Copyright (C) 2021 Eric Truett
# Licensed under the MIT License

from pathlib import Path
from typing import Any, List

import numpy as np
import polars as pl

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap, QFont
from PySide6.QtWidgets import (QFormLayout, QLabel, QTableView, QHBoxLayout, QHeaderView, QSizePolicy, QWidget, 
                               QVBoxLayout, QToolButton, QWidget, QStyle, QFileDialog, QLineEdit)

from pyqtconfig import ConfigManager
from pangadfs_gui.model import DataframeModel
from pangadfs_gui.view import DataframeView


class DataframeWidget(QWidget):
    def __init__(self, model: DataframeModel, fn: str = None):
        """Creates widget
        
        Args:
            model (DataframeModel): the model for the widget
            fn (str): optional, will load dataframe if passed

        Returns:
            DataframeWidget

        """
        super().__init__()

        # Getting the Model
        self.model = model
        if fn:
            self.model.loadCsv(fn)

        # Creating a QTableView
        self.table_view = DataframeView(self.model)

        # DataframeWidget Layout
        self.main_layout = QHBoxLayout()
        size = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        size.setHorizontalStretch(0)
        self.table_view.setSizePolicy(size)
        self.main_layout.addWidget(self.table_view)
        self.setLayout(self.main_layout)


class ButtonStripWidget(QWidget):
    """Base button strip widget"""
    def __init__(self, buttons: List[dict] = None, margins: tuple = None, alignment: Qt.Alignment = None):
        super().__init__()
        self.main_layout = QHBoxLayout()
        if buttons:
            for button in buttons:
                self.main_layout.add(self._make_button(button))
        if margins:
            self.main_layout.setContentsMargins(margins)
        if alignment:
            self.main_layout.setAlignment(alignment)

    def _make_button(self, data):
        """Makes button given values in data"""
        b = QToolButton()
        if 'tooltip' in data:
            b.setToolTip(data.get('tooltip'))
        if 'connect' in data:
            b.clicked.connect(data.get('connect'))
        if 'icon' in data:
            if data['icon'][0] == ':':
                b.setIcon(QIcon(QPixmap(data['icon'])))
            else:
                b.setIcon(self.style().standardIcon(getattr(QStyle.StandardPixmap, data['icon'])))


class TabWidget(QWidget):
    """Base 2-column widget for tabs"""
    def __init__(self, config: ConfigManager):
        super().__init__()
        self.main_layout = QVBoxLayout()
        self.button_strip = ButtonStripWidget()
        self.dataframe_widget = DataframeWidget(model=DataframeModel(df=None))
        self.main_layout.addWidget(self.button_strip)
        self.main_layout.addWidget(self.dataframe_widget)
        self.setLayout(self.main_layout)


class SidebarConfigWidget(QWidget):
    def __init__(self, config: ConfigManager, label: str = 'Settings', margins: tuple = (0, 12, 0, 5), alignment: Qt.Alignment = Qt.AlignTop):
        super().__init__()
        self.config = config
        self.main_layout = QVBoxLayout()
        
        # label widget
        self.sub_layout = QHBoxLayout()
        label = QLabel()
        label.setText(label)
        lFont = QFont()
        lFont.setBold(True)
        label.setFont(lFont)
        label.setLayout(self.sub_layout)

        # form layout is for config editing
        self.form_layout = QFormLayout()
        cols = self.config.as_dict().keys()
        self.mapping = {col: QLineEdit() for col in cols}
        for label, widget in self.mapping.items():
            self.form_layout.addRow(label, widget)

        # add to main layout
        self.main_layout.addLayout(self.sub_layout, 1)
        self.main_layout.addLayout(self.form_layout, 99)
        self.setLayout(self.main_layout)