"""
Module with variable objects

    Classes
    ------------
    Variables: set of Time, Flow and Effort variables
        RotationalVariables: Implementation of Variables in rotational domain
        LinearVariables: Implementation of Variables in translational domain
        ElectricalVariables: Implementation of Variable in rotational domain

"""

from __future__ import annotations
from typing import TYPE_CHECKING
from abc import ABC, abstractmethod
from dataclasses import dataclass
import numpy as np
from scipy import integrate

if TYPE_CHECKING:
    from dozersim.modelling import Model
    from dozersim.path import Path


class Variables(ABC):
    """ Class that contains flow, effort and time variables
        they are generalized variables that are domain independent
        Rotational domain: Effort = Torque and Flow = Speed
        Linear domain: Effort = Force and Flow = Velocity
        Electrical domain: Effort = Voltage and Flow = Current
        Note the only flow and effort are stored in the variable set
        generalized displacement, acceleration and power are calculated

        Attributes
        -----------
            name (str): Name of the variable set
            time (ndarray): Time series
            effort (ndarray): sum of all efforts
            torque (ndarray): alias for effort
            force (ndarray): alias for effort
            voltage (ndarray): alias for effort
            flow (ndarray): sum of all flows
            velocity (ndarray): alias of flow
            current (ndarray): alias of flow
            power (ndarrat): effort*flow1

        Methods
        -----------
            add: add variable to variable set
            get_all_flows: return all flows
            get_all_efforts: return list of efforts

    """
    __slots__ = ('parent', 'name', '_time', 'efforts', 'flows', '_load_case')

    def __init__(self, parent: Path, name: str = "FEV", old_vars: Variables = None) -> None:
        self.name: str = name
        self.parent = parent
        self._time: Time = old_vars._time if old_vars else None
        self.efforts: list[Effort] = []
        self.flows: list[Flow] = []
        self._load_case: str | None = None

    @property
    def time(self):
        try:
            # normal case were time is defined
            time = self._time.data
        except AttributeError:
            # support for static analysis
            time = np.array([0])
        return time

    @property
    def effort(self) -> np.ndarray:
        """ Return total effort variable as ndarray"""
        efforts = np.array([effort.data for effort in self.efforts])
        return efforts.sum(axis=0)

    @property
    def torque(self) -> np.ndarray:
        """ Alias for effort"""
        return self.effort

    @property
    def force(self) -> np.ndarray:
        """ Alias for effort"""
        return self.effort

    @property
    def voltage(self) -> np.ndarray:
        """ Alias for effort"""
        return self.effort

    @property
    def displacement(self) -> np.ndarray:
        """ Return generalized displacement as ndarray"""
        flows = np.array([flow.data[0] for flow in self.flows])
        return flows.sum(axis=0)

    @property
    def flow(self) -> np.ndarray:
        """ Return total flow as ndarray"""
        flows = np.array([flow.data[1] for flow in self.flows])
        return flows.sum(axis=0)

    @property
    def velocity(self) -> np.ndarray:
        """ Alias for flow """
        return self.flow

    @property
    def current(self) -> np.ndarray:
        """ Alias for flow """
        return self.flow

    @property
    def acceleration(self) -> np.ndarray:
        """ Return generalized acceleration as ndarray"""
        flows = np.array([flow.data[2] for flow in self.flows])
        return flows.sum(axis=0)

    @property
    def power(self) -> np.ndarray:
        """ Return power as ndarray"""
        return self.flow * self.effort

    @property
    def energy(self) -> np.ndarray:
        """ Return power as ndarray"""
        return integrate.cumulative_trapezoid(self.power, self.time, initial=0)

    def add(self, target: str, values: np.ndarray, parent: Model, name: str):
        """ Returns a dictionary with function to add data to the variables

            target
            ------------
            'effort': np.ndarray
                describes the torque, voltage, voltage etc.
            'torque':
                torque series
            'force':
            'displacement':
            'charge':
            'flow':
            'velocity':
            'current':
            'acceleration':
            'current_rate':
            'time':

        """
        self._setters[target](values, parent, name)

    @property
    def _setters(self) -> dict[str,callable]:
        return {'effort': self._add_effort,
                'torque': self._add_effort,
                'force': self._add_effort,
                'voltage': self._add_effort,
                'displacement': self._add_state0,
                'charge': self._add_state0,
                'flow': self._add_state1,
                'velocity': self._add_state1,
                'current': self._add_state1,
                'acceleration': self._add_state2,
                'current_rate': self._add_state2,
                'time': self._add_time
                }

    def _add_effort(self, values: np.ndarray, parent: Model, name: str):
        """ Add variable to container
                Parameters
                ------------
                    variable (Variable): variables that need to be added to variables set
        """
        effort = Effort(name, parent, values)
        self.efforts.append(effort)

    def _add_state0(self, values: np.ndarray, parent: Model, name: str):
        """ Add variable to container
            Parameters
            ------------
            values
            parent
            name

        """
        data = {0: None, 1: None, 2: None}
        data[0] = values
        try:
            # add a series of values and calculate other states by gradient
            data[1] = np.gradient(values, self.time.data)
            data[2] = np.gradient(data[1], self.time.data)
        except (ValueError, IndexError):
            # single value was obtained probably a static analysis
            data[1] = np.array([0])
            data[2] = np.array([0])

        flow = Flow(name, parent, data)
        self.flows.append(flow)

    def _add_state1(self, values: np.ndarray, parent: Model, name: str, init0: float = 0):
        """ Add variable to container
            Parameters
            ------------
            values
            parent
            name
            order

        """
        data = {0: None, 1: None, 2: None}
        data[1] = values
        try:
            # add a series of values and calculate other states by gradient or integrate
            data[0] = integrate.cumulative_trapezoid(values, self.time.data, initial=init0)
            data[2] = np.gradient(values, self.time.data)
        except (ValueError, IndexError):
            # single value was obtained probably a static analysis
            data[0] = np.array([0])
            data[2] = np.array([0])

        flow = Flow(name, parent, data)
        self.flows.append(flow)

    def _add_state2(self, values: np.ndarray, parent: Model, name: str, init1: float = 0, init0: float = 0):
        """ Add variable to container
            Parameters
            ------------
            values
            parent
            name
            init0
            init1

        """
        data = {0: None, 1: None, 2: None}
        data[2] = values
        try:
            # add a series of values and calculate other states by integrate
            data[1] = integrate.cumulative_trapezoid(values, self.time.data, initial=init1)
            data[0] = integrate.cumulative_trapezoid(data[1], self.time.data, initial=init0)
        except (ValueError, IndexError):
            # single value was obtained probably a static analysis
            data[1] = np.array([0])
            data[0] = np.array([0])

        flow = Flow(name, parent, data)
        self.flows.append(flow)

    def _add_time(self, values: np.ndarray, model: Model, name: str):
        """ Add variable to container
            Parameters
            ------------
            variable (Variable): variables that need to be added to variables set

        """
        self._time = Time(name, model, values)

    @property
    @abstractmethod
    def state0_label(self) -> str:
        """ Returns flow units"""
        pass

    @property
    @abstractmethod
    def state1_label(self) -> str:
        """ Returns flow units"""
        pass

    @property
    @abstractmethod
    def state2_label(self) -> str:
        """ Returns flow units"""
        pass

    @property
    @abstractmethod
    def effort_label(self) -> str:
        """ Returns effort units"""
        pass

    @property
    def load_case(self) -> str:
        return self._load_case

    @load_case.setter
    def load_case(self, val: str):
        self._load_case = val

    @property
    @abstractmethod
    def domain(self):
        pass

    def __repr__(self) -> str:
        return f"Variables({self.name})"


class RotationalVariables(Variables):
    """ Variables in the rotational domain
    implements specific properties of linear variables like label and units"""
    __slots__ = ()

    def __init__(self, parent: Path, name: str = "Rotational FEV", old_vars: Variables = None) -> None:
        super().__init__(parent, name, old_vars)

    @property
    def state1_label(self) -> str:
        return 'Speed in rad/s'

    @property
    def state0_label(self) -> str:
        return 'Angle in rad'

    @property
    def state2_label(self) -> str:
        return 'Acceleration in rad'

    @property
    def effort_label(self) -> str:
        return 'Torque in Nm'

    @property
    def domain(self):
        return 'rotational'

    def __repr__(self) -> str:
        return f"RotationalVariables({self.name})"


class TranslationalVariables(Variables):
    """ Variables in the linear domain
    implements specific properties of linear variables like label and units"""
    __slots__ = ()

    def __init__(self, parent: Path, name: str = "Linear FEV", old_vars: Variables = None) -> None:
        super().__init__(parent, name, old_vars)

    @property
    def state1_label(self) -> str:
        return 'Speed in m/s'

    @property
    def state0_label(self) -> str:
        return 'Distance in m'

    @property
    def state2_label(self) -> str:
        return 'Acceleration in m/s^2'

    @property
    def effort_label(self) -> str:
        return 'Force in N'

    @property
    def domain(self):
        return 'translational'

    def __repr__(self) -> str:
        return f"LinearVariables({self.name})"


class ElectricalVariables(Variables):
    """ Variables in the electrical domain
    implements specific properties of linear variables like label and units
    """
    __slots__ = ()

    def __init__(self, parent: Path, name: str = "Electrical FEV", old_vars: Variables = None) -> None:
        super().__init__(parent, name, old_vars)

    @property
    def state1_label(self) -> str:
        return 'Current in A'

    @property
    def state0_label(self) -> str:
        return 'Charge in J'

    @property
    def state2_label(self) -> str:
        return 'Rate of current in A/s'

    @property
    def effort_label(self) -> str:
        return 'Voltage in V'

    @property
    def domain(self):
        return 'electrical'

    def __repr__(self) -> str:
        return f"ElectricalVariables({self.name})"


@dataclass(slots=True)
class Variable(ABC):
    name: str
    parent: Model
    data: any


@dataclass(slots=True)
class Flow(Variable):
    data: dict[int, np.ndarray]


@dataclass(slots=True)
class Effort(Variable):
    data: np.ndarray


@dataclass(slots=True)
class Time(Variable):
    data: np.ndarray
