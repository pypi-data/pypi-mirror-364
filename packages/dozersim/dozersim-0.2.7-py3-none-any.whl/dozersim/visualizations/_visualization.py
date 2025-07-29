from __future__ import annotations
import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QTableWidget, \
    QTableWidgetItem, QHBoxLayout, QLabel, QSpinBox, QPushButton
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from typing import TYPE_CHECKING

from dozersim.visualizations._plotting import create_plot
from dozersim.visualizations._plotting import get_variable_plot

if TYPE_CHECKING:
    from dozersim.results import Analysis, Result


app = QApplication(sys.argv)


class Visualization(QMainWindow):
    def __init__(self, parent=None, title: str = "Dozer simulation gui"):
        super().__init__()
        self.setWindowTitle(title)
        self.current_window = -1
        self.tabs_main = QTabWidget()
        self.setCentralWidget(self.tabs_main)
        self.resize(1280, 900)
        self._analyses: list[Analysis] = []
        self._analyses_windows: list[AnalysisWindows] = []
        self.show()

    @property
    def analysis(self):
        return self._analyses[-1]

    def add_analysis(self, analysis: Analysis):
        self._analyses.append(analysis)
        analysis_tab = AnalysisWindows(analysis=analysis)
        self.tabs_main.addTab(analysis_tab, f'analysis {len(self._analyses)}')
        self._analyses_windows.append(analysis_tab)

    def add_plot(self, x_object: Parameter | Objective,
                 y_object: Parameter | Objective,
                 z_object: Parameter | Objective = None,
                 plot_type: str = 'line'):
        self._analyses_windows[-1].add_plot(x_object, y_object, z_object, plot_type)


class AnalysisWindows(QTabWidget):

    def __init__(self, analysis: Analysis, parent=None):
        super().__init__(parent)
        self.additional_plots = []
        self._analysis = analysis
        self.result_tabs = ResultWindow(result=analysis.results[-1])

        #  self.plot_variables()
        var_tab = QWidget()
        self.addTab(var_tab, 'Results')
        layout = QVBoxLayout()
        var_tab.setLayout(layout)

        bar = QWidget()
        label = QLabel()
        label.setText(f'Select set between 1 and {len(self._analysis.results)}:')
        self.pushButton = QPushButton()
        self.pushButton.setText('Confirm selection')
        self.pushButton.setMaximumWidth(150)
        self.pushButton.clicked.connect(self.update_plots)
        self.spinBox = QSpinBox()
        self.spinBox.setMinimum(1)
        self.spinBox.setMaximum(len(self._analysis.results))
        # spinBox.setPrefix('set ')
        # spinBox.setSuffix(f' of {len(self._analysis.results)}')
        self.spinBox.setMaximumWidth(150)
        self.spinBox.setMinimumWidth(100)
        bar_layout = QHBoxLayout()
        bar_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        bar_layout.addWidget(label)
        bar_layout.addWidget(self.spinBox)
        bar_layout.addWidget(self.pushButton)
        bar.setLayout(bar_layout)
        layout.addWidget(bar)
        layout.addWidget(self.result_tabs)
        headers, data = analysis.analysis_table()
        self.addTab(MyTable(headers=headers, data=data), 'Sets')

    def update_plots(self):
        idx = self.spinBox.value()
        self.result_tabs.update_results(self._analysis.results[idx - 1])

    def add_plot(self, x_object, y_object, z_object=None,
                 plot_type: str = 'line'):
        fig = create_plot(self._analysis, x_object, y_object, z_object, plot_type)
        self.additional_plots.append(fig)
        self.addTab(MyPlot(fig=fig), f'plot {len(self.additional_plots)}')


class ResultWindow(QTabWidget):

    def __init__(self, result: Result, parent=None):
        super().__init__(parent)
        self.plots: dict[tuple, MyPlot] = {}
        self.tables: dict[str, MyTable] = {}
        for load_case in result.load_cases:
            path_tabs = QTabWidget()
            for path in result.paths:
                if path is not None:
                    variables = result.get_variables(load_case, path)
                    variable_tabs = QTabWidget()
                    for var in variables:
                        plot = MyPlot(fig=get_variable_plot(var))
                        variable_tabs.addTab(plot, var.name)
                        self.plots.update({(load_case, path, var.name): plot})
                    path_tabs.addTab(variable_tabs, path.name)
            headers, data = result.result_table(load_case=load_case)
            table = MyTable(headers=headers, data=data)
            path_tabs.addTab(table, 'Results')
            self.tables.update({load_case: table})
            self.addTab(path_tabs, load_case)

    def update_results(self, result: Result):
        for load_case in result.load_cases:
            for path in result.paths:
                if path is not None:
                    variables = result.get_variables(load_case, path)
                    for var in variables:
                        get_variable_plot(var, fig=self.plots[(load_case, path, var.name)].sc.figure)
                        self.plots[(load_case, path, var.name)].sc.figure.canvas.draw_idle()
            headers, data = result.result_table(load_case=load_case)
            self.tables[load_case].update_table(headers, data)


class MyPlot(QWidget):

    def __init__(self, parent=None, fig: Figure = None):
        super().__init__()
        self.sc = FigureCanvas(figure=fig)
        layout = QVBoxLayout()
        self.setLayout(layout)
        new_toolbar = NavigationToolbar(self.sc)
        layout.addWidget(self.sc)
        layout.addWidget(new_toolbar)



def show_plots():
    app.exec()


class MyTable(QWidget):
    def __init__(self, headers, data, parent=None):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.table = QTableWidget()
        self.table.setRowCount(len(data))
        self.table.setColumnCount(len(data[0]))
        for i, row in enumerate(data):
            for j, item in enumerate(row):
                q_item = QTableWidgetItem(item)
                self.table.setItem(i, j, q_item)
        # table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        self.table.setHorizontalHeaderLabels(headers)
        self.table.move(0, 0)
        layout.addWidget(self.table)

    def update_table(self, headers, data):
        self.table.clear()
        self.table.setRowCount(len(data))
        self.table.setColumnCount(len(data[0]))
        for i, row in enumerate(data):
            for j, item in enumerate(row):
                q_item = QTableWidgetItem(item)
                self.table.setItem(i, j, q_item)
        # table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        self.table.setHorizontalHeaderLabels(headers)
        self.table.move(0, 0)
