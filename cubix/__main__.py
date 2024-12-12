import sys

from PyQt5 import QtWidgets

from .playground import Playground

app = QtWidgets.QApplication(sys.argv)
plotter = Playground()
plotter.show()
sys.exit(app.exec_())
