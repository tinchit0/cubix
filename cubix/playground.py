import matplotlib.patches as mpatches
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from PyQt5 import QtCore, QtGui, QtWidgets

import cubix

SLIDER_MAXIMUM = 100

CLASSES_COLORS = {
    0: "red",
    1: "green",
    2: "fuchsia",
    3: "blue",
    4: "turquoise",
    5: "lime",
    6: "purple",
    7: "gold",
    8: "brown",
    9: "navy",
}

MAX_COLORS = len(CLASSES_COLORS)


class DataPlot(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        self.fig = Figure()
        self.fig.suptitle("Data plot")
        FigureCanvasQTAgg.__init__(self, self.fig)
        self.axes = self.fig.gca()
        self.setParent(parent)


class PersistenceDiagramPlot(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        fig = Figure()
        fig.suptitle("Persistence diagram")
        self.axes = fig.add_subplot(111)
        FigureCanvasQTAgg.__init__(self, fig)
        self.setParent(parent)
        self.compute_initial_figure()
        self.set_lims()
        self.draw()

    @property
    def colors(self):
        return {0: "blue", 1: "green", 2: "orange", 3: "red"}

    def compute_initial_figure(self):
        self.axes.plot((0, 1), (0, 1), color="gray")

    def bars(self, n):
        self.axes.plot((n, n), (0, n), color="red")
        self.axes.plot((0, n), (n, n), color="red")

    def set_lims(self):
        self.axes.set_xlim([-0.05, 1.05])
        self.axes.set_ylim([-0.05, 1.05])

    def set_legend(self, n):
        self.axes.legend(
            handles=[
                mpatches.Patch(color=self.colors[dim], label="H%d" % dim)
                for dim in range(n)
            ],
            loc=4,
        )


class Playground(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setDefault()
        self.setScreen()
        self.setFiltration()

    def setData(self):
        # TO DO: Data selection
        # self.cloud = cubix.clouds.T2(N=1000, b=10)
        # --------------
        self.setFiltration()
        if self.cloud.dimension == 2:
            self.show_kde_checkbox.setEnabled(True)
        if self.cloud.dimension == 3:
            self.show_kde_checkbox.setChecked(False)
            self.show_kde_checkbox.setEnabled(False)

    def setFiltration(self):
        self.grid_precission = int(self.grid_precission_input.text())
        self.margin = float(self.margin_input.text())
        self.pruning = float(self.pruning_input.text())
        if float(self.bandwidth_input.text()) == 0:
            self.cloud.kde.set_bandwidth(bw_method="scott")
        else:
            self.cloud.kde.set_bandwidth(bw_method=float(self.bandwidth_input.text()))
        self.filtration = cubix.utils.Filtration(
            self.cloud, self.grid_precission, self.margin, self.pruning
        )
        self.homology = cubix.utils.PersistentHomology(self.filtration)
        self.setClassColors()
        self.plot()

    def setClassColors(self):
        self.class_color = {}
        for dim in range(self.cloud.dimension + 1):
            for i, hclass in enumerate(self.homology.holes[dim]):
                self.class_color[hclass] = CLASSES_COLORS[i % MAX_COLORS]

    def plot(self):
        # Persistence diagram
        self.persistence_diagram.axes.clear()
        n = self.filtration_slider.value() / float(SLIDER_MAXIMUM)
        self.persistence_diagram.compute_initial_figure()
        for dim in range(self.cloud.dimension + 1):
            for hclass in self.homology.holes[dim]:
                if hclass.born > n:
                    continue
                x = [hclass.born, hclass.born]
                y = [hclass.born, min(hclass.death, n)]
                self.persistence_diagram.axes.plot(
                    x, y, linewidth=2.0, color=self.persistence_diagram.colors[dim]
                )
        self.persistence_diagram.bars(n)
        self.persistence_diagram.set_lims()
        self.persistence_diagram.set_legend(self.cloud.dimension)
        self.persistence_diagram.draw()

        # Data plot
        if self.cloud.dimension == 2:
            self.plot2d()
        if self.cloud.dimension == 3:
            self.plot3d()

    def plot2d(self):
        self.data_plot.axes.clear()
        if self.show_kde_checkbox.isChecked():
            self.kde_precission = int(self.kde_precission_input.text())
            grid = cubix.utils.Grid(self.cloud, self.kde_precission, self.margin)
            kernel = self.cloud.kde
            x, y = grid.mesh
            z = grid.evaluate(kernel)
            self.data_plot.axes.pcolor(x, y, z, cmap="RdPu", vmin=0)
        if self.show_data_checkbox.isChecked():
            x, y = self.cloud.data
            self.data_plot.axes.scatter(x, y, color="black")
        if self.show_grid_checkbox.isChecked():
            x, y = self.filtration.grid.mesh
            self.data_plot.axes.scatter(x, y, marker="x", alpha=0.5, color="gray")
            # for cube in self.filtration[1]:
            #     if cube.dimension == 0:
            #         x, y = self.filtration.grid[cube.root]
            #         self.data_plot.axes.plot(x, y, 'ro', color='blue', alpha=(1-cube.value)**2)
            #         self.data_plot.axes.plot(x, y, 'ro', color='gray')
        if self.show_filtration_checkbox.isChecked():
            n = self.filtration_slider.value() / float(SLIDER_MAXIMUM)
            for cube in self.filtration[n]:
                if cube.dimension == 0:
                    x, y = self.filtration.grid[cube.root]
                    self.data_plot.axes.plot(x, y, "ro", color="gray")
                if cube.dimension == 1:
                    x1, y1 = self.filtration.grid[cube.points[0]]
                    x2, y2 = self.filtration.grid[cube.points[1]]
                    self.data_plot.axes.plot([x1, x2], [y1, y2], color="gray")
                if cube.dimension == 2:
                    x1, y1 = self.filtration.grid[cube.points[0]]
                    x2, y2 = self.filtration.grid[cube.points[3]]
                    self.data_plot.axes.add_patch(
                        Rectangle(
                            (x1, y1),
                            x2 - x1,
                            y2 - y1,
                            hatch="//",
                            fill=False,
                            color="gray",
                        )
                    )
        # xlim, ylim = self.filtration.grid.size
        # self.data_plot.axes.set_xlim(xlim)
        # self.data_plot.axes.set_ylim(ylim)
        # self.data_plot.axes.axis('equal')

        # Make equal axis with a fake bounding box
        max_range = max([M - m for m, M in self.filtration.grid.size])
        average = [0.5 * (m + M) for m, M in self.filtration.grid.size]
        Xb = (
            0.5 * max_range * np.mgrid[-1:2:2, -1:2:2, -1:2:2][0].flatten() + average[0]
        )
        Yb = (
            0.5 * max_range * np.mgrid[-1:2:2, -1:2:2, -1:2:2][1].flatten() + average[1]
        )
        for xb, yb in zip(Xb, Yb):
            self.data_plot.axes.plot([xb], [yb], "w")

        self.data_plot.draw()

    def plot3d(self):
        self.data_plot.axes = self.data_plot.fig.add_subplot(111, projection="3d")
        self.data_plot.axes.clear()
        if self.show_data_checkbox.isChecked():
            x, y, z = self.cloud.data
            self.data_plot.axes.scatter(x, y, z, c="black")
        if self.show_grid_checkbox.isChecked():
            # x, y, z = self.filtration.grid.mesh
            # self.data_plot.axes.scatter(x, y, z, marker='x', alpha=0.5, c='gray')
            for cube in self.filtration[1]:
                if cube.dimension == 0:
                    x, y, z = self.filtration.grid[cube.root]
                    self.data_plot.axes.plot(
                        [x], [y], [z], "ro", c="blue", alpha=(1 - cube.value) ** 2
                    )
        if self.show_filtration_checkbox.isChecked():
            n = self.filtration_slider.value() / float(SLIDER_MAXIMUM)
            for cube in self.filtration[n]:
                if cube.dimension == 0:
                    x, y, z = self.filtration.grid[cube.root]
                    self.data_plot.axes.plot([x], [y], [z], "ro", c="gray")
                if cube.dimension == 1:
                    x1, y1, z1 = self.filtration.grid[cube.points[0]]
                    x2, y2, z2 = self.filtration.grid[cube.points[1]]
                    self.data_plot.axes.plot([x1, x2], [y1, y2], [z1, z2], color="gray")
                # if cube.dimension == 2:
                #     x1, y1, z1 = self.filtration.grid[cube.points[0]]
                #     x2, y2, z2 = self.filtration.grid[cube.points[3]]
                #     if z1 == z2:
                #         rectangle = Rectangle((x1, y1), x2-x1, y2-y1, hatch='//', fill=False, color='gray')
                #         self.data_plot.axes.add_patch(rectangle)
                #         art3d.pathpatch_2d_to_3d(rectangle, z=z1, zdir="z")
                #     if y1 == y2:
                #         rectangle = Rectangle((x1, z1), x2-x1, z2-z1, hatch='//', fill=False, color='gray')
                #         self.data_plot.axes.add_patch(rectangle)
                #         art3d.pathpatch_2d_to_3d(rectangle, z=y1, zdir="y")
                #     if x1 == x2:
                #         rectangle = Rectangle((y1, z1), y2-y1, z2-z1, hatch='//', fill=False, color='gray')
                #         self.data_plot.axes.add_patch(rectangle)
                #         art3d.pathpatch_2d_to_3d(rectangle, z=x1, zdir="x")
                # if cube.dimension == 3:
                #     verts = [[self.filtration.grid[point] for point in s.points] for s in cube.border()]
                #     for face in verts:
                #         aux = face[2][:]
                #         face[2] = face[3]
                #         face[3] = aux
                #     self.data_plot.axes.add_collection3d(Poly3DCollection(verts, facecolors='gray', alpha=.25))
        # xlim, ylim, zlim = self.filtration.grid.size
        # self.data_plot.axes.set_xlim(xlim)
        # self.data_plot.axes.set_ylim(ylim)
        # self.data_plot.axes.set_zlim(zlim)
        self.data_plot.axes.set_xlabel("x")
        self.data_plot.axes.set_ylabel("y")
        self.data_plot.axes.set_zlabel("z")
        # Make equal axis with a fake bounding box
        max_range = max([M - m for m, M in self.filtration.grid.size])
        average = [0.5 * (m + M) for m, M in self.filtration.grid.size]
        Xb = (
            0.5 * max_range * np.mgrid[-1:2:2, -1:2:2, -1:2:2][0].flatten() + average[0]
        )
        Yb = (
            0.5 * max_range * np.mgrid[-1:2:2, -1:2:2, -1:2:2][1].flatten() + average[1]
        )
        Zb = (
            0.5 * max_range * np.mgrid[-1:2:2, -1:2:2, -1:2:2][2].flatten() + average[2]
        )
        for xb, yb, zb in zip(Xb, Yb, Zb):
            self.data_plot.axes.plot([xb], [yb], [zb], "w")
        self.data_plot.draw()

    def setDefault(self):
        self.cloud = cubix.clouds.S1(N=1000, err=0.1)
        self.grid_precission = 10
        self.kde_precission = 50
        self.margin = 0.1
        self.pruning = 0

    def setScreen(self):
        self.setWindowTitle("Plotter")
        self.resize(1087, 697)

        # *** OPTIONS ***
        self.options_group = QtWidgets.QGroupBox(self)
        self.options_group.setGeometry(QtCore.QRect(680, 20, 390, 340))
        self.options_group.setTitle("Options")
        # Select Data Button
        self.select_data_group = QtWidgets.QGroupBox(self.options_group)
        self.select_data_group.setGeometry(QtCore.QRect(0, 0, 400, 80))
        self.select_data_button = QtWidgets.QPushButton(self.select_data_group)
        self.select_data_button.setGeometry(QtCore.QRect(40, 35, 121, 27))
        self.select_data_button.setText("Select Data")
        self.select_data_button.clicked.connect(self.setData)
        # Parameters
        self.parameters_group = QtWidgets.QGroupBox(self.options_group)
        self.parameters_group.setGeometry(QtCore.QRect(0, 60, 400, 150))
        # -- > Grid precission
        self.grid_precission_label = QtWidgets.QLabel(self.parameters_group)
        self.grid_precission_label.setGeometry(QtCore.QRect(20, 30, 110, 30))
        self.grid_precission_label.setText("Grid Precission:")
        self.grid_precission_input = QtWidgets.QLineEdit(self.parameters_group)
        self.grid_precission_input.setGeometry(QtCore.QRect(150, 30, 50, 27))
        self.grid_precission_input.setValidator(QtGui.QIntValidator(0, 10000))
        self.grid_precission_input.setText(str(self.grid_precission))
        self.grid_precission_input.editingFinished.connect(self.setFiltration)
        # --> KDE precission
        self.kde_precission_label = QtWidgets.QLabel(self.parameters_group)
        self.kde_precission_label.setGeometry(QtCore.QRect(20, 70, 110, 30))
        self.kde_precission_label.setText("KDE precission:")
        self.kde_precission_input = QtWidgets.QLineEdit(self.parameters_group)
        self.kde_precission_input.setGeometry(QtCore.QRect(150, 70, 50, 27))
        self.kde_precission_input.setValidator(QtGui.QIntValidator(0, 10000))
        self.kde_precission_input.setText(str(self.kde_precission))
        self.kde_precission_input.editingFinished.connect(self.plot)
        # --> Margin
        self.margin_label = QtWidgets.QLabel(self.parameters_group)
        self.margin_label.setGeometry(QtCore.QRect(220, 30, 110, 30))
        self.margin_label.setText("Margin:")
        self.margin_input = QtWidgets.QLineEdit(self.parameters_group)
        self.margin_input.setGeometry(QtCore.QRect(330, 30, 50, 27))
        self.margin_input.setValidator(QtGui.QDoubleValidator(0.0, 1.0, 5))
        self.margin_input.setText(str(self.margin))
        self.margin_input.editingFinished.connect(self.setFiltration)
        # --> Prune
        self.pruning_label = QtWidgets.QLabel(self.parameters_group)
        self.pruning_label.setGeometry(QtCore.QRect(220, 70, 110, 30))
        self.pruning_label.setText("Pruning:")
        self.pruning_input = QtWidgets.QLineEdit(self.parameters_group)
        self.pruning_input.setGeometry(QtCore.QRect(330, 70, 50, 27))
        self.pruning_input.setValidator(QtGui.QDoubleValidator(0.0, 1.0, 5))
        self.pruning_input.setText(str(self.pruning))
        self.pruning_input.editingFinished.connect(self.setFiltration)
        # --> Bandwidth
        self.bandwidth_label = QtWidgets.QLabel(self.parameters_group)
        self.bandwidth_label.setGeometry(QtCore.QRect(220, 110, 110, 30))
        self.bandwidth_label.setText("Bandwidth:")
        self.bandwidth_input = QtWidgets.QLineEdit(self.parameters_group)
        self.bandwidth_input.setGeometry(QtCore.QRect(330, 110, 50, 27))
        self.bandwidth_input.setValidator(QtGui.QDoubleValidator(0.0, 1.0, 5))
        self.bandwidth_input.setText(str(self.pruning))
        self.bandwidth_input.editingFinished.connect(self.setFiltration)
        # Show options
        self.show_options_group = QtWidgets.QGroupBox(self.options_group)
        self.show_options_group.setGeometry(QtCore.QRect(0, 190, 400, 90))
        self.show_label = QtWidgets.QLabel(self.show_options_group)
        self.show_label.setGeometry(QtCore.QRect(30, 30, 68, 17))
        self.show_label.setText("Show")
        # --> Data
        self.show_data_checkbox = QtWidgets.QCheckBox(self.show_options_group)
        self.show_data_checkbox.setGeometry(QtCore.QRect(10, 55, 70, 22))
        self.show_data_checkbox.setText("Data")
        self.show_data_checkbox.setChecked(True)
        self.show_data_checkbox.stateChanged.connect(self.plot)
        # --> KDE
        self.show_kde_checkbox = QtWidgets.QCheckBox(self.show_options_group)
        self.show_kde_checkbox.setGeometry(QtCore.QRect(80, 55, 65, 22))
        self.show_kde_checkbox.setText("KDE")
        self.show_kde_checkbox.stateChanged.connect(self.plot)
        # --> Grid
        self.show_grid_checkbox = QtWidgets.QCheckBox(self.show_options_group)
        self.show_grid_checkbox.setGeometry(QtCore.QRect(145, 55, 65, 22))
        self.show_grid_checkbox.setText("Grid")
        self.show_grid_checkbox.stateChanged.connect(self.plot)
        # --> Filtration
        self.show_filtration_checkbox = QtWidgets.QCheckBox(self.show_options_group)
        self.show_filtration_checkbox.setGeometry(QtCore.QRect(210, 55, 100, 22))
        self.show_filtration_checkbox.setText("Filtration")
        self.show_filtration_checkbox.stateChanged.connect(self.plot)
        # --> Classes
        self.show_classes_checkbox = QtWidgets.QCheckBox(self.show_options_group)
        self.show_classes_checkbox.setGeometry(QtCore.QRect(310, 55, 80, 22))
        self.show_classes_checkbox.setText("Classes")
        self.show_classes_checkbox.stateChanged.connect(self.plot)
        self.show_classes_checkbox.setEnabled(False)  # Not longer implemented
        # Filtration slider
        self.filtration_group = QtWidgets.QGroupBox(self.options_group)
        self.filtration_group.setGeometry(QtCore.QRect(0, 260, 400, 80))
        self.filtration_label = QtWidgets.QLabel(self.filtration_group)
        self.filtration_label.setGeometry(QtCore.QRect(30, 30, 71, 17))
        self.filtration_label.setText("Filtration:")
        self.filtration_slider = QtWidgets.QSlider(self.filtration_group)
        self.filtration_slider.setGeometry(QtCore.QRect(10, 35, 370, 50))
        self.filtration_slider.setOrientation(QtCore.Qt.Horizontal)
        self.filtration_slider.setMinimum(0)
        self.filtration_slider.setMaximum(SLIDER_MAXIMUM)
        self.filtration_slider.valueChanged.connect(self.plot)

        # *** PLOTS ***
        # Main plot (data)
        self.data_plot = DataPlot(self)
        self.data_plot.setGeometry(QtCore.QRect(10, 10, 650, 671))
        # Persistence diagram
        self.persistence_diagram = PersistenceDiagramPlot(self)
        self.persistence_diagram.setGeometry(QtCore.QRect(680, 370, 390, 310))
