from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, TYPE_CHECKING, Any

import numpy as np
from pint import UnitRegistry

from dozersim.parameters import DatabaseLink
if TYPE_CHECKING:
    from dozersim.path import Path
    from dozersim.variables import Variables
    from dozersim.modelling import Model
    from dozersim.constraints import Constraint
    from dozersim.parameters import Parameter
    from dozersim.objectives import Objective


class Result:

    def __init__(self):
        self._variables: list[Variables] = []
        self._result_objects: list[ResultObject] = []
        self.id: int = 0

    def add_result_objects(self, load_case: int | None, variable_list: list[Variables] = None, result_objs: list[
        ResultObject] = None):
        # add load case label and store result objects and variables
        if variable_list is not None:
            for var in variable_list:
                var.load_case = load_case
                self._variables.append(var)
        if result_objs is not None:
            for res in result_objs:
                res.load_case = load_case
                self._result_objects.append(res)

    @property
    def constraints(self) -> list[ConstraintValue]:
        return [result_obj for result_obj in self._result_objects if type(result_obj) is ConstraintValue]

    @property
    def costs(self) -> list[ObjectiveValue]:
        return [result_obj for result_obj in self._result_objects if type(result_obj) is ObjectiveValue]

    def get_result_objects(self, load_case: str = None, path: Path = None) -> list[ResultObject]:
        res_list = self._result_objects
        if load_case is not None:
            res_list = list(filter(lambda obj: obj.load_case == load_case, res_list))
        if path is not None:
            res_list = list(filter(lambda obj: obj.path == path, res_list))
        return res_list

    def get_variables(self, load_case: str = None, path: Path = None) -> list[Variables]:
        var_list = self._variables
        if load_case is not None:
            var_list = list(filter(lambda obj: obj.load_case == load_case, var_list))
        if path is not None:
            var_list = list(filter(lambda obj: obj.parent == path, var_list))
        return var_list

    @property
    def load_cases(self) -> set[str]:
        return {obj.load_case for obj in self._result_objects}.union({obj.load_case for obj in self._variables})

    @property
    def paths(self) -> set[Path]:
        return {obj.path for obj in self._result_objects}.union({obj.parent for obj in self._variables})

    def activate(self):
        for obj in self._result_objects:
            if isinstance(obj, ParameterValue):
                obj.parent.default_vals = obj.value
                obj.parent.reset()

    @property
    def result_table(self, load_case: str = None, path: Path = None) -> (list[str], list[list[str]]):
        # Compile a flat list of all parameters, costs and constraints
        data = []
        headers = ['Type', 'Load case', 'Path', 'Name', 'Value', 'Limit']
        for result_obj in self.get_result_objects(load_case, path):
            value = f'{result_obj.value:.4f}' if isinstance(result_obj.value, float) else result_obj.value
            path_name = result_obj.path.name if result_obj.path is not None else 'None'
            data.append([type(result_obj).__name__, result_obj.load_case, path_name, result_obj.name, value, result_obj.limits])
        return headers, data


def get_non_iterable(parameters: list[Parameter]):
    return tuple(filter(lambda parameter: not isinstance(parameter, Iterable), parameters))


def get_iterable(parameters: list[Parameter]):
    return tuple(filter(lambda parameter: isinstance(parameter, Iterable), parameters))


class Analysis:

    def __init__(self):
        self.results: list[Result] = []
        self._active_id: int = 0

    def add_result(self, result: Result):
        self.results.append(result)

    @property
    def load_cases(self) -> list[str]:
        return list(self.results[-1].load_cases)

    def get_result_values(self, load_case: str,
                          target_obj: Parameter | Objective) -> list:
        values = []
        for result in self.results:
            for res in result.get_result_objects(load_case):
                if res.parent is target_obj:
                    values.append(res.value)
        return values

    def activate_set(self, idx: int):
        result = self.result_dict[idx]
        result.activate()
        self._active_id = idx

    @property
    def result_dict(self) -> dict[int, Result]:
        return {result.id: result for result in self.results}

    def get_fittest_set(self, load_case: str, objective: Objective) -> int:
        # idx = list(np.flatnonzero(cost == np.min(cost)))
        fittest_val = float('inf')
        fittest_set = None
        for idx, result in self.result_dict.items():
            for obj in result.get_result_objects(load_case):
                if obj.parent is objective and obj.evaluate() < fittest_val:
                    fittest_val = obj.evaluate()
                    fittest_set = idx
        return fittest_set

    @property
    def analysis_table(self) -> (list[str], list[list[str]]):
        data = []
        headers = ['Set ID']
        headers.extend([obj.name for obj in self.results[0].get_result_objects() if isinstance(obj, ParameterValue) or isinstance(obj, ObjectiveValue)])
        for result in self.results:
            row = [f'{result.id:003}']
            for obj in result.get_result_objects():
                if isinstance(obj, ParameterValue) or isinstance(obj, ObjectiveValue):
                    value = f'{obj.value:.4f}' if isinstance(obj.value, float) else obj.value
                    row.append(value)
            data.append(row)
        return headers, data


ureg = UnitRegistry()


class ResultObject(ABC):

    def __init__(self, path: Path = None):
        self.path: Path | None = path
        self.load_case: str | None = None
        self.parent: Any = None

    @property
    @abstractmethod
    def value(self):
        pass

    @property
    @abstractmethod
    def limits(self):
        pass

    @property
    @abstractmethod
    def name(self):
        pass


class Load(ResultObject):

    def __init__(self, parent: Model, path: 'Path', force_axial: np.ndarray, force_radial: np.ndarray):
        super().__init__(path=path)
        self.force_axial = force_axial
        self.force_radial = force_radial
        self.parent = parent

    @property
    def value(self):
        return np.max([np.max(np.abs(self.force_radial)), np.max(np.max(self.force_axial))])

    @property
    def limits(self):
        return ''

    @property
    def name(self):
        return self.parent.name


class ConstraintValue(ResultObject):

    def __init__(self, path: Path, parent: Constraint, model: Model, value: float,
                 lb: float = float('-inf'), ub: float = float('inf')):
        super().__init__(path=path)
        self.parent = parent
        self.model = model
        self._value = value
        self.unit: str = ''
        self.lb = lb
        self.ub = ub

    @property
    def value(self):
        return self._value

    def evaluate(self):
        return np.max([self.value / self.ub - 1, self.value / self.lb - 1])

    @property
    def limits(self):
        return f'{self.lb:.4f} ... {self.ub:.4f}'

    @property
    def name(self):
        return f'{self.model.name}.{self.parent.name}'


class ObjectiveValue(ResultObject):

    def __init__(self, path: Path, parent: Objective, unit: str, value: float):
        super().__init__(path=path)
        self.parent = parent
        self._value = value
        self.unit: str = ''

    def evaluate(self):
        return self.value * self.parent.goal * self.parent.scale

    @property
    def value(self):
        return self._value

    @property
    def limits(self):
        return ''

    @property
    def name(self):
        return self.parent.name


class ParameterValue(ResultObject):

    def __init__(self, parent: Parameter, value: float, path: Path = None):
        super().__init__(path=path)
        self.parent = parent
        self._value = value
        self.unit: str = ''

    @property
    def name(self):
        return self.parent.name

    @property
    def limits(self):
        return self.parent.limits

    @property
    def value(self):
        if type(self.parent) is DatabaseLink:
            return self._value.name
        else:
            return self._value

    @value.setter
    def value(self, value: Any):
        self._value = value
