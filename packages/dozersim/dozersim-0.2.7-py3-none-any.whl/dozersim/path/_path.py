"""
Module: path_management

This module defines the `Path` class, which models the energy flow of a system
and manages variables and analysis associated with it. A `Path` acts as a
builder that creates variable objects, handles transformations, and contains
travelers of various types.

Classes
-------
Path
    Represents a path object that maps the energy flow of the modeled system.

Attributes
----------
fev_dict : dict
    A mapping of energy domains ('rotational', 'translational', 'electrical')
    to their respective variable classes.

Usage Example
-------------
>>> from dozersim.path import Path
>>> path = Path("rotational", "RotationalPath")
>>> path.transform("electrical", "ElectricalTransform")
>>> variables, analysis = path.unload()
"""

from __future__ import annotations

import dozersim.results
from dozersim import variables
from typing import List, Any, TYPE_CHECKING
from dozersim.results import ResultObject, ConstraintValue, ObjectiveValue
import logging


logger = logging.getLogger(__name__)

fev_dict = {
    'rotational': variables.RotationalVariables,
    'translational': variables.TranslationalVariables,
    'electrical': variables.ElectricalVariables
}


class Path:
    """
    Represents a paths object that maps the energy flow of the modeled system.
    A `Path` can create and transform variable objects and contains travelers
    of various types such as analysis and constraints.

    Attributes
    ----------
    name : str
        Name of the paths.
    verbose : bool
        Indicates whether verbose output is enabled.
    travelers : list
        List of travelers (e.g., loads, constraints).
    _variables : list[_variables.Variables]
        List of variables representing the energy flow in the paths.
    _start_type : str
        Initial domain type ('rotational', 'translational', 'electrical').

    Methods
    -------
    reset()
        Clears the paths's variables and travelers.
    get_result_object(*travtype: type | tuple) -> List
        Retrieves a list of travelers of specified types.
    add_result_object(traveler: analysis.Load | analysis.ConstraintValue | analysis.ObjectiveValue)
        Adds a traveler to the paths.
    transform(var_type: str, name: str)
        Transforms the energy flow to a new domain by creating a new variable set.
    unload() -> tuple[list[variables.Variables], list[Any]]
        Unloads and returns all variables and travelers, then resets the paths.
    check(var_type: str)
        Checks if the latest variable set matches the specified domain type.
    variables -> variables.Variables
        Returns the latest variable set.
    """

    def __init__(self, start_type: str, name: str = "Path", static: bool = False) -> None:
        """
        Initializes a new Path instance.

        Parameters
        ----------
        start_type : str
            Initial domain type ('rotational', 'translational', 'electrical').
        name : str, optional
            Name of the paths (default is "Path").
        """
        self.name: str = name
        self.static = static
        self.verbose = False
        self._variables: list[variables.Variables] = []
        self._start_type = start_type
        self.travelers: list = []
        self.reset()

    def reset(self):
        """
        Clears the paths's variables and travelers, and resets it to its initial state.
        """
        self._variables = [fev_dict[self._start_type](self, name='source')]
        self.travelers = []

    def get_result_object(self, *travtype: type | tuple) -> List[ResultObject]:
        """
        Retrieves a list of travelers of the specified types.

        Parameters
        ----------
        travtype : type or tuple
            Types of travelers to retrieve (e.g., Load, ConstraintValue, ObjectiveValue).

        Returns
        -------
        list
            List of travelers matching the specified types.
        """
        return list(filter(lambda traveler: isinstance(traveler, travtype), self.travelers))

    def add_result_object(self, traveler: ResultObject):
        """
        Adds a traveler to the paths.

        Parameters
        ----------
        traveler : Load | ConstraintValue | ObjectiveValue
            The traveler to add.
        """
        self.travelers.append(traveler)

    def transform(self, var_type: str, name: str):
        """
        Transforms the energy flow by creating a new set of variables.
        Acts as a transformer if the domain matches the previous one, or as a
        gyrator if it changes domains.

        Parameters
        ----------
        var_type : str
            New domain type ('rotational', 'translational', 'electrical').
        name : str
            Name of the new variable set.
        """
        variable_type = fev_dict[var_type]
        if self._variables:
            variables = variable_type(parent=self, name=name, old_vars=self._variables[-1])
        else:
            variables = variable_type(parent=self, name=name)
        self._variables.append(variables)

    def unload(self) -> tuple[list[variables.Variables], list[Any]]:
        """
        Unloads and returns all variables and result objects, then resets the paths.

        Returns
        -------
        tuple
            variables : list[variables.Variables]
                List of all flow and effort variables.
            result_objects : list[Any]
                List of all constraints and objective values.
        """
        variables = self._variables
        result_objects = self.get_result_object(dozersim.results._results.ObjectiveValue,
                                                dozersim.results._results.ConstraintValue)
        return variables, result_objects

    def check(self, var_type: str):
        """
        Checks if the latest variable set matches the specified domain type.

        Parameters
        ----------
        var_type : str
            Domain type to check ('rotational', 'translational', 'electrical').

        Raises
        ------
        Exception
            If the domain type does not match.
        """
        if not isinstance(self._variables[-1], fev_dict[var_type]):
            raise Exception("You're in the wrong domain!")

    @property
    def variables(self) -> variables.Variables:
        """
        Returns the latest variable set.

        Returns
        -------
        _variables.Variables
            The latest variable set.
        """
        return self._variables[-1]

    def __repr__(self) -> str:
        """
        Returns a string representation of the paths.

        Returns
        -------
        str
            String representation of the paths.
        """
        return f"Path({self.name})"
