from pathlib import Path
import sys

import pandas as pd

from PySide6.QtWidgets import (QTableView, QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QHeaderView, QSizePolicy,
                               QTableView, QToolButton, QTreeWidget, QWidget, QFileDialog, QTabWidget)
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QAction, QKeySequence, QIcon


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


class PandasModel(QAbstractTableModel):
    """A model to interface a Qt view with pandas dataframe """

    def __init__(self, dataframe: pd.DataFrame, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self._dataframe = dataframe

    def rowCount(self, parent=QModelIndex()) -> int:
        """ Override method from QAbstractTableModel

        Return row count of the pandas DataFrame
        """
        if parent == QModelIndex():
            return len(self._dataframe)

        return 0

    def columnCount(self, parent=QModelIndex()) -> int:
        """Override method from QAbstractTableModel

        Return column count of the pandas DataFrame
        """
        if parent == QModelIndex():
            return len(self._dataframe.columns)
        return 0

    def data(self, index: QModelIndex, role=Qt.ItemDataRole):
        """Override method from QAbstractTableModel

        Return data cell from the pandas DataFrame
        """
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            return str(self._dataframe.iloc[index.row(), index.column()])

        return None

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole
    ):
        """Override method from QAbstractTableModel

        Return dataframe index as vertical header data and columns as horizontal header data.
        """
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._dataframe.columns[section])

            if orientation == Qt.Vertical:
                return str(self._dataframe.index[section])

        return None

    def sort(self, Ncol, order):
        """Sort table by given column number.
        """
        try:
            self.layoutAboutToBeChanged.emit()
            if order == Qt.DescendingOrder:
                ascending = False
            elif order == Qt.AscendingOrder:
                ascending = True
            self._dataframe = self._dataframe.sort_values(self._dataframe.columns[Ncol], ascending=ascending)
            self.layoutChanged.emit()
        except Exception as e:
            print(e)


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

        self.horizontal_header = self.table_view.horizontalHeader()
        self.horizontal_header.setSectionResizeMode(
                               QHeaderView.ResizeToContents
                             )
        self.horizontal_header.setStretchLastSection(True)

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
        butt2 = QToolButton()
        butt1.setArrowType(Qt.DownArrow)
        butt2.setArrowType(Qt.UpArrow)
        t1_1_layout.addWidget(butt1)
        t1_1_layout.addWidget(butt2)
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


class MainWindowOld(QMainWindow):

    def __init__(self, widget):
        QMainWindow.__init__(self)
        self.setWindowTitle("Lineup Explorer")
        self.setCentralWidget(widget)

        # Status Bar
        self.status = self.statusBar()

        # create menus
        self.create_menus()

        # Window dimensions
        geometry = self.screen().availableGeometry()
        self.setFixedSize(geometry.width() * 0.4, geometry.height() * 0.3)

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
        widget = PandasWidget(df)
        self.setCentralWidget(widget)
        self.update()
        self.status.showMessage("Data loaded.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('fusion')
    #widget = PandasWidget(pd.read_csv('data.csv'))
    #window = MainWindow(widget)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())