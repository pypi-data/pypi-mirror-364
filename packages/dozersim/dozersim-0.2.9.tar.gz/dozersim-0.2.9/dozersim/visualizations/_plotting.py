from __future__ import annotations
import matplotlib
import numpy as np
from typing import TYPE_CHECKING
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

if TYPE_CHECKING:
    from dozersim.results import Analysis


from dozersim.parameters import Parameter
from dozersim.objectives import Objective

matplotlib.use('QtAgg')


def get_variable_plot(var, fig: Figure = None) -> Figure:
    if fig is not None:
        axs = fig.axes
        for ax in axs:
            ax.cla()
    else:
        fig, axs = plt.subplots(4, sharex='col')  # .add_subplot(111)
    nflows = 0
    n_efforts = 0
    for flow in var.flows:
        axs[0].plot(var.time, flow.data[0], label=flow.name)
        axs[0].grid(True)
        axs[0].set_ylabel(var.state0_label)
        axs[0].set_title(f"FEV: {var.name}")
        axs[1].plot(var.time, flow.data[1], label=flow.name)
        axs[1].grid(True)
        axs[1].set_ylabel(var.state1_label)
        # axs[0].set_title(f"FEV: {var.name}")
        nflows += 1
    if nflows > 1:
        axs[1].plot(var.time, var.flow, label='Total')
    axs[1].legend()
    for effort in var.efforts:
        axs[2].plot(var.time, effort.data, label=effort.name)
        axs[2].grid(True)
        axs[2].set_ylabel(var.effort_label)
        n_efforts += 1
    if n_efforts > 1:
        axs[2].plot(var.time, var.effort, label='Total')
    axs[2].legend()
    if (nflows > 0) & (n_efforts > 0):
        axs[3].plot(var.time, var.power)
        axs[3].grid(True)
        axs[3].set_ylabel('Power in W')
        axs[3].set_xlabel('Time in s')

    return fig


def plot_results_2d(analysis: Analysis,
                    x_object: Parameter | Objective,
                    y_object: Parameter | Objective | list,
                    *args, **kwargs) -> Figure:
    """
    Plot the x results with respect to y results

    Parameters
    ----------
    y_object
    x_object

    Returns
    -------

    """
    fig, ax = plt.subplots()  # .add_subplot(111)

    for load_case in analysis.load_cases:
        x_data = np.array(analysis.get_result_values(load_case, x_object))
        y_data = np.array(analysis.get_result_values(load_case, y_object))
        '''
        if type(y_object) is not list:
            y_object = [y_object]
        for obj in y_object:
            y_data = np.array(analysis.get_result_series(load_case, obj))
            plt.plot(x_data, y_data, label=load_case.name)
        '''
        ax.plot(x_data, y_data, label=load_case)
        ax.set_ylabel(y_object.name)
        ax.set_xlabel(x_object.name)
        ax.legend()
        plt.suptitle(f"Load case {load_case}")
    return fig

    # for load_case in analysis.load_cases:
    #    headers, data = analysis.get_result_sets(load_case)


def plot_results_3d(analysis: Analysis,
                    x_object: Parameter | Objective,
                    y_object: Parameter | Objective,
                    z_object: Parameter | Objective) -> Figure:
    """
    Plot 3D surface to x, y and z result objects

    Parameters
    ----------
    analysis :
    z_object
    y_object
    x_object

    Returns
    -------

    """
    fig, ax = plt.subplots(1, 1, subplot_kw={'projection': '3d'})
    for load_case in analysis.load_cases:
        x_data = np.array(analysis.get_result_values(load_case, x_object))
        y_data = np.array(analysis.get_result_values(load_case, y_object))
        x_length = len(list(x_object))
        y_length = len(list(y_object))
        x_data = x_data.reshape((x_length, y_length))
        y_data = y_data.reshape((x_length, y_length))
        z_data = np.array(analysis.get_result_values(load_case, z_object))
        z_data = z_data.reshape((x_length, y_length))

        ax.set_xlabel(x_object.name)
        ax.set_ylabel(y_object.name)
        ax.set_zlabel(z_object.name)
        ax.plot_surface(x_data, y_data, z_data, rstride=1, cstride=1, cmap='viridis', edgecolor='none')
        #ax.plot_trisurf(x_data, y_data, z_data, cmap=cm.jet, linewidth=0.1)
        ax.legend()
        plt.draw()

    return fig


def plot_results_scatter(analysis: Analysis, x_object: Objective,
                         y_object: Objective,
                         *args, **kwargs) -> Figure:
    """
    Plot the x, y scatter of the result sets

    Parameters
    ----------
    analysis
    y_object
    x_object

    Returns
    -------

    """
    fig, ax = plt.subplots()
    legend_texts = []

    for load_case in analysis.load_cases:
        x_data = np.array(analysis.get_result_values(load_case, x_object))
        y_data = np.array(analysis.get_result_values(load_case, y_object))

        ax.scatter(np.round(x_data, 2), np.round(y_data, 2))

        set_label = 1
        for x_val, y_val in zip(x_data, y_data):
            ax.annotate(f'Set {set_label}', (x_val, y_val))
            set_label += 1

        legend_texts.append(load_case)

    ax.set_xlabel(x_object.name)
    ax.set_ylabel(y_object.name)
    ax.legend(legend_texts)
    plt.suptitle(f"Trade off")

    return fig


def create_plot(analysis: Analysis, x_object, y_object, z_object=None,
                plot_type: str = 'line'):
    z_data_present = issubclass(type(z_object), (Parameter | Objective))
    fig = plot_dict[z_data_present, plot_type](analysis, x_object, y_object, z_object)
    return fig


plot_dict = {
    (False, 'line'): plot_results_2d,
    (False, 'scatter'): plot_results_scatter,
    (True, 'line'): plot_results_3d
}
