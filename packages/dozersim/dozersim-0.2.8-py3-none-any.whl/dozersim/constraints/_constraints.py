from __future__ import annotations
from typing import TYPE_CHECKING
from abc import ABC, abstractmethod

from dozersim.utils import target_dict, statistic_dict

if TYPE_CHECKING:
    from dozersim.modelling import Model, Settings
    from dozersim.path import Path

from dozersim.results import ConstraintValue


class Constraint(ABC):

    def __init__(self, name: str, lb: str | float = None, ub: str | float = None, settings: Settings = None, scale: float = 1) -> None:
        self.lb = lb
        self.ub = ub
        self.name = name
        self._settings: Settings = settings
        self._optimize = True

    @abstractmethod
    def evaluate(self, model: Model, path: Path, value: float = None):
        pass

    @property
    def optimize(self):
        pass

    def get_bound_kws(self, model: Model) -> dict:
        bounds = dict()
        for kw in {'ub', 'lb'}:
            # check if lb and ub are defined
            if isinstance(self.__getattribute__(kw), str):
                try:
                    bound_val = model.settings.get_setting(self.__getattribute__(kw))
                    if bound_val is not None:
                        bounds[kw] = bound_val
                except AttributeError:
                    raise Exception('Settings object not present and/or keyword for bound incorrect!')
            elif self.ub is float:
                bounds[kw] = self.ub
        return bounds


class PathConstraint(Constraint):

    def __init__(self, name: str, statistic: str, target: str, settings: Settings,
                 lb: str | float = None, ub: str | float = None, scale: float = 1) -> None:
        super().__init__(name, lb, ub, settings, scale)
        self._target = target_dict[target]
        self._statistic = statistic_dict[statistic]
        self._optimize = True

    @property
    def optimize(self):
        return self._optimize

    @optimize.setter
    def optimize(self, do_optimize: bool):
        self._optimize = do_optimize

    def evaluate(self, model: Model, path: Path, value: float = None):

        values = self._target.evaluate(path)
        value = self._statistic.evaluate(values)
        kws = self.get_bound_kws(model)
        path.add_result_object(
            ConstraintValue(parent=self, model=model, value=value, path=path, **kws))


class CustomConstraint(Constraint):

    def __init__(self, name: str, settings: Settings = None, lb: str | float = None, ub: str | float = None,
                 scale: float = 1) -> None:
        super().__init__(name, lb, ub, settings, scale)
        self._settings: Settings = settings
        self._optimize = True

    @property
    def optimize(self):
        return self._optimize

    @optimize.setter
    def optimize(self, do_optimize: bool):
        self._optimize = do_optimize

    def evaluate(self, model: Model, path: Path, value: float = None):
        kws = self.get_bound_kws(model)
        path.add_result_object(
            ConstraintValue(parent=self, model=model, value=value, path=path, **kws))
