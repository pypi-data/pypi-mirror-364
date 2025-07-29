from __future__ import annotations

from typing import List, Any, TYPE_CHECKING
from abc import ABC, abstractmethod
from sqlalchemy.orm import Query
import numpy as np
import copy

from dozersim.suppliers import session

if TYPE_CHECKING:
    from dozersim.modelling import Settings


class Parameter(ABC):
    """
    Parameter abstract class

    """

    def __init__(self, name: str, default_vals: Any):
        self.name = name
        self.default_vals = default_vals

    def reset(self):
        self.set_value(self.default_vals)

    @abstractmethod
    def set_value(self, value: Any):
        pass

    @property
    @abstractmethod
    def limits(self):
        pass

    @property
    @abstractmethod
    def trace(self):
        pass


class SettingsParameter(Parameter):
    """ Parameter class stores a handle of a settings object.
    when x0 is set, the parameters becomes an optimization parameter
    when num is set, the simulation iterates the parameter

        Attributes
        -----------
        name (str): name of the parameter
        lb (float): lower bound
        ub (float): upper bound
        x0 (float): starting point
        num (int): number of interactions
    """

    def __init__(self, name: str, settings: List[Settings] | Settings, keywords: List[str] | str,
                 lb: float = -10e5, ub: float = 10e5, x0: float = None, num: int = None, scale: float = 1):
        """
            Parameter
        """
        self.lb = lb
        self.ub = ub
        self.x0 = x0
        self.num = num
        if x0 is not None and num is not None:
            raise Exception('x0 and num cannot be specified at the same time!')
        elif x0 is None and num is None:
            raise Exception('Either x0 or num have to be specified!')
        self.scale = scale
        if type(settings) is not list: settings = [settings]
        self._settings: List[Settings] = settings
        self._keywords: List[str] = []
        if type(keywords) is not list: keywords = [keywords]
        [self._keywords.append(keyword) for keyword in keywords]
        default_vals = read_from_settings(settings, keywords)
        super().__init__(name, default_vals)

    @property
    def trace(self):
        trace_set = set()
        trace_set.update([type(setting).__name__+'.'+keyword for setting, keyword in zip(self._settings,self._keywords)])
        return f"{'+'.join(list(trace_set))}"

    def __iter__(self):
        if self.num is not None:
            return np.linspace(self.lb, self.ub, self.num).__iter__()
        else:
            return None

    def set_value(self, value):
        write_to_settings(self._settings, self._keywords, value*self.scale)

    @property
    def limits(self):
        return f'{self.lb:.4f} ... {self.ub:.4f}'


def write_to_settings(settings: List[Settings], keywords: List[str], value: Any | List[Any]):
    if type(value) is list:
        for setting, keyword, value in zip(settings, keywords, value):
            setting.set_setting(keyword, value)
    else:
        for setting, keyword in zip(settings, keywords):
            setting.set_setting(keyword, value)


def read_from_settings(settings: List[Settings], keywords: List[str]) -> list:
    return [setting.get_setting(keyword) for setting, keyword in zip(settings, keywords)]


class DatabaseLink(Parameter):
    """ 
    Adapter that couples settings (Settings) to a database table
    
    """

    def __init__(self, settings: Settings, name: str = "New supplier link"):
        self._settings: Settings = settings
        if settings.supplier_table:
            self._table = settings.supplier_table
        else:
            raise Exception("No supplier table linked to this setting class! Implement the supplier_table getter "
                            "method.")
        self._query: Query
        self.reset_query()
        default_vals = copy.deepcopy(settings)
        super().__init__(name=name, default_vals=default_vals)

    def __iter__(self):
        return self._query.__iter__()

    @property
    def trace(self):
        return type(self._settings).__name__

    def list_table(self):
        for entry in self._query:
            print(f"Table entry {entry.name}")

    def set_value(self, value: Query | str | Settings):
        while True:
            if type(value) is str:
                value = self._query.filter_by(name=value).first()
            else:
                for attr in [val for val in value.__dict__.keys() if '_sa_' not in val]:
                    setattr(self._settings, attr, getattr(value, attr))
                break

    @property
    def query(self) -> Query:
        return self._query

    @query.setter
    def query(self, query: Query):
        self._query = query

    def reset_query(self):
        self._query = session.query(self._table)

    @property
    def limits(self):
        return ''

