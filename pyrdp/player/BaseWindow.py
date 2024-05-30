#
# This file is part of the PyRDP project.
# Copyright (C) 2018-2023 GoSecure Inc.
# Licensed under the GPLv3 or later.
#

import logging
from typing import Dict

from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QTabWidget, QWidget

from pyrdp.logging import LOGGER_NAMES


class BaseWindow(QTabWidget):
    """
    Class that encapsulates the common logic to manage a QtTabWidget to display RDP connections,
    regardless of their origin (network or file).
    """

    def __init__(self, options: Dict[str, object], parent: QWidget = None, maxTabCount = 250):
        super().__init__(parent)
        self.maxTabCount = maxTabCount
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.onTabCloseRequest)
        self.log = logging.getLogger(LOGGER_NAMES.PLAYER)
        self.options = options

        # close Tab
        closeTabAction = QAction("Close Tab", self)
        closeTabAction.setShortcut(QKeySequence("Ctrl+W"))
        closeTabAction.triggered.connect(self.onCtrlW)
        self.addAction(closeTabAction)

    def onTabClosed(self, index: int):
        """
        Gracefully closes the tab by calling the onClose method
        :param index: Index of the closed tab
        """
        tab = self.widget(index)
        tab.onClose()
        self.removeTab(index)


    def onTabCloseRequest(self, index: int):
        """
        By default, will close the tab. Can be overriden to add validation.
        """

        self.onTabClosed(index)

    def onCtrlW(self):
        if self.options.get("closeTabOnCtrlW") and self.count() > 0:
            self.onTabCloseRequest(self.currentIndex())
