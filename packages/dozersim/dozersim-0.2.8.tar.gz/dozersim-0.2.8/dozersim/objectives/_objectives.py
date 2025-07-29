from __future__ import annotations
from typing import TYPE_CHECKING
from abc import ABC, abstractmethod

import numpy as np

from dozersim.utils import target_dict, statistic_dict

if TYPE_CHECKING:
    from dozersim.modelling import Model
    from dozersim.path import Path

from dozersim.results import ObjectiveValue, ConstraintValue


class Objective(ABC):

    def __init__(self, statistic: str, goal: str,
                 scale: float = 1) -> None:
        self.statistic = statistic_dict[statistic]
        self.goal = goal_dict[goal]
        self.scale = scale
        self._optimize = True

    @abstractmethod
    def engage(self):
        pass

    @abstractmethod
    def disengage(self):
        pass

    @abstractmethod
    def evaluate(self, paths: tuple[Path]):
        pass

    @property
    def name(self):
        pass

    @property
    def optimize(self):
        pass

    @property
    @abstractmethod
    def trace(self):
        pass


class SettingsObjective(Objective):
    """
    The SettingsObjective class is and implementation of Object that collects settings with a certain keyword.

    """

    def __init__(self, models: Model | list[Model], statistic: str, goal: str,
                 target: str, scale: float = 1) -> None:
        super().__init__(statistic, goal, scale)
        if type(models) is not list: models = [models]
        self._models = models
        self.target = target
        self._optimize = False

    @property
    def name(self):
        return f'{self.statistic.name()} {self.target}'

    @property
    def trace(self):
        return self._models.name

    @property
    def optimize(self):
        return self._optimize

    @optimize.setter
    def optimize(self, do_optimize: bool):
        if do_optimize:
            raise Warning("Dragons ahead! Setting a SettingsObjective to be optimized, can cause unstable behavior "
                          "since settings objective can be highly discontinuous.")
        self._optimize = do_optimize

    def engage(self):
        self._models[-1].post_eval.append(self.evaluate)

    def disengage(self):
        self._models[-1].post_eval.remove(self.evaluate)

    def evaluate(self, paths):

        setting_values = []

        if isinstance(self._models, list):
            models = self._models
        elif isinstance(self._models, Model):
            models = [self._models]
        else:
            raise Exception('Component object in objective function is not an instance of model or list of models')

        for model in models:
            try:
                value = model.settings.get_setting(self.target)
            except AttributeError:
                pass
            else:
                setting_values.append(value)

        if len(setting_values) == 0:
            raise Exception(
                f'Setting {self.target} not found in object-scope. Please check items of remove objective')

        cost_value = self.statistic.evaluate(np.array(setting_values))
        paths[0].add_result_object(
            ObjectiveValue(parent=self, unit='', value=cost_value, path=paths[0]))


class ConstraintObjective(Objective):
    """
    The Constraint Objective class is an implementation of Objective
    """

    def __init__(self, model: Model, goal: str,
                 target: str, scale: float = 1) -> None:
        super().__init__('None', goal, scale)
        self._model = model
        self._target = target
        self._optimize = False

    @property
    def name(self):
        return f'{self._model.name}.{self._target}'

    @property
    def trace(self):
        return self._model.name

    @property
    def optimize(self):
        return self._optimize

    @optimize.setter
    def optimize(self, do_optimize: bool):
        self._optimize = do_optimize

    def engage(self):
        self._model.post_eval.append(self.evaluate)

    def disengage(self):
        self._model.post_eval.remove(self.evaluate)

    def evaluate(self, paths: tuple[Path] = ()):
        for path in paths:
            const_objs: list[ConstraintValue] = path.get_result_object(ConstraintValue)
            for const_obj in const_objs:
                if const_obj.model == self._model and const_obj.parent.name == self._target:
                    cost_value = const_obj.value
                    path.travelers.remove(const_obj)
                    path.add_result_object(
                        ObjectiveValue(parent=self, unit=const_obj.unit, value=cost_value, path=path))


class PathObjective(Objective):

    def __init__(self, model: Model, statistic: str, target: str, goal: str,
                 scale: float = 1, path: Path = None) -> None:
        super().__init__(statistic, goal, scale)
        self.target = target_dict[target]
        self._model = model
        self._path = path
        self._optimize = True

    @property
    def name(self):
        return f'{self._model.name}.{self.statistic.name()} {self.target.name()}'

    @property
    def trace(self):
        return self._model.name

    @property
    def optimize(self):
        return self._optimize

    @optimize.setter
    def optimize(self, do_optimize: bool):
        self._optimize = do_optimize

    def engage(self):
        self._model.post_eval.append(self.evaluate)

    def disengage(self):
        self._model.post_eval.remove(self.evaluate)

    def evaluate(self, paths: tuple[Path]):
        if self._path and (self._path in paths):
            path = self._path
        else:
            path, = paths

        cost_values = self.target.evaluate(path)
        cost_value = self.statistic.evaluate(cost_values)

        path.add_result_object(
            ObjectiveValue(parent=self, unit=self.target.units(path), value=cost_value, path=path))


goal_dict = {'maximize': -1,
             'minimize':  1}
