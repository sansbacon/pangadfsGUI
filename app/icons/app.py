# pangadfsgui/app/app.py
# -*- coding: utf-8 -*-
# Copyright (C) 2021 Eric Truett
# Licensed under the MIT License

import sys 

from PySide6.QtWidgets import QApplication
from pangadfs_gui.main import MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec())