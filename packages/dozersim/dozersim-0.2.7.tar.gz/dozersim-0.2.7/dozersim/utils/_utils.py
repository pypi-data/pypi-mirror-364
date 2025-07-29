from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
import numpy as np
from prettytable import PrettyTable

if TYPE_CHECKING:
    from dozersim import path


def print_table(headers, data):
    table = PrettyTable(headers)
    table.add_rows(data)
    print(table)


class Target(ABC):

    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def evaluate(self, path: path.Path) -> np.ndarray:
        pass

    @abstractmethod
    def units(self, path: path.Path) -> str:
        pass


class PowerTarget(Target):

    def evaluate(self, path: path.Path):
        return path.variables.power

    def units(self, path: path.Path) -> str:
        return "in W"

    def name(self):
        return 'Power'


class EnergyTarget(Target):

    def evaluate(self, path: path.Path):
        return path.variables.energy

    def units(self, path: path.Path) -> str:
        return " in J"

    def name(self):
        return 'Energy'


class EffortTarget(Target):

    def evaluate(self, path: path.Path):
        return path.variables.effort

    def units(self, path: path.Path) -> str:
        return path.variables.effort_label

    def name(self):
        return 'Effort'


class FlowTarget(Target):

    def evaluate(self, path: path.Path):
        return path.variables.flow

    def units(self, path: path.Path) -> str:
        return path.variables.state1_label

    def name(self):
        return 'Flow'


class Statistic(ABC):

    @abstractmethod
    def evaluate(self, values: np.ndarray) -> float:
        pass

    @abstractmethod
    def name(self):
        pass


class Minium(Statistic):

    def evaluate(self, values: np.ndarray):
        return np.min(values)

    def name(self):
        return 'Minimum'


class Maximum(Statistic):

    def evaluate(self, values: np.ndarray):
        return np.max(values)

    def name(self):
        return 'Maximum'


class AbsoluteMinimum(Statistic):

    def evaluate(self, values: np.ndarray):
        return np.min(np.abs(values))

    def name(self):
        return 'AbsoluteMinimum'


class AbsoluteMaximum(Statistic):

    def evaluate(self, values: np.ndarray):
        return np.max(np.abs(values))

    def name(self):
        return 'AbsoluteMaximum'


class Mean(Statistic):

    def evaluate(self, values: np.ndarray):
        return np.mean(values)

    def name(self):
        return 'Mean'


class AbsoluteMean(Statistic):

    def evaluate(self, values: np.ndarray):
        return np.mean(np.abs(values))

    def name(self):
        return 'AbsoluteMean'


class Sum(Statistic):

    def evaluate(self, values: np.ndarray):
        return np.sum(values)

    def name(self):
        return 'Sum'


class SumOfAbsolutes(Statistic):

    def evaluate(self, values: np.ndarray):
        return np.sum(np.abs(values))

    def name(self):
        return 'abssum'


class Nothing(Statistic):

    def evaluate(self, values: np.ndarray):
        return values

    def name(self):
        return 'none'


target_dict = {'power':  PowerTarget(),
               'flow':   FlowTarget(),
               'effort': EffortTarget(),
               'energy': EnergyTarget()}
statistic_dict = {'None': Nothing(),
                  'absmax': AbsoluteMaximum(),
                  'absmin': AbsoluteMinimum(),
                  'max':    Maximum(),
                  'min':    Minium(),
                  'sum':    Sum(),
                  'abssum': SumOfAbsolutes(),
                  'mean': Mean(),
                  'absmean': AbsoluteMean()}
