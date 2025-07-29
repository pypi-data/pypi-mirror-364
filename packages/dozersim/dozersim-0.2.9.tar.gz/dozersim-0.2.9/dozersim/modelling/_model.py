"""
This module defines the `Model` class, an abstract base class representing
a simulation model with configurable settings, evaluation functions, and constraints.

Classes
-------
Model
    Abstract base class for creating simulation models.
"""
from __future__ import annotations
from abc import ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dozersim.modelling import Settings
    from dozersim.path import Path
    from dozersim.constraints import Constraint


class Model(ABC):
    """Abstract base class representing a simulation model.

    Attributes
    ----------
    name : str
        Name of the model.
    _settings : Settings
        Simulation settings object.
    _eval_fun : callable
        Evaluation function to run simulations.
    post_eval : list[callable]
        List of post-evaluation functions.
    _constraints : dict[str, Constraint]
        Dictionary storing constraints by name.
    """

    def __init__(self, eval_fun: callable, name: str, settings: Settings) -> None:
        """Initializes the Model with evaluation function, name, and settings.

        Parameters
        ----------
        eval_fun : callable
            Function used to evaluate paths.
        name : str
            Name of the model.
        settings : Settings
            Simulation settings object.
        """
        self.name = name
        self._settings = settings
        self._eval_fun = eval_fun
        self.post_eval: list[callable] = []
        self._constraints: dict[str, Constraint] = {}

    def __repr__(self) -> str:
        """Returns a string representation of the Model.

        Returns
        -------
        str
            A representation string showing the model's name and settings.
        """
        return f'settings.Lead("{self.name}", function, settings)'

    def __str__(self) -> str:
        """Returns the model's name as a string.

        Returns
        -------
        str
            The model's name.
        """
        return self.name

    @property
    def settings(self) -> Settings:
        """Gets the current simulation settings.

        Returns
        -------
        Settings
            The current simulation settings object.
        """
        return self._settings

    @settings.setter
    def settings(self, settings: Settings):
        """Sets new simulation settings.

        Parameters
        ----------
        settings : Settings
            New simulation settings object.

        """
        self._settings = settings

    def evaluate(self, paths: list[Path]):
        """Evaluates paths using the evaluation function and settings.

        Parameters
        ----------
        paths : list[Path]
            List of paths to evaluate.
        """
        self._eval_fun(paths, self._settings, self)
        for fun in self.post_eval:
            fun(paths)

    def add_constraint(self, constraint: Constraint):
        """Adds a constraint to the internal constraint dictionary.

        Parameters
        ----------
        constraint : constraints.Constraint
            The constraint to add. Its name is used as the dictionary key.
        """
        cons_name = constraint.name
        self._constraints[cons_name] = constraint

    @property
    def constraints(self):
        """Retrieves all constraints in the internal dictionary.

        Returns
        -------
        dict[str, constraints.Constraint]
            Dictionary mapping constraint names to `Constraint` objects.
        """
        return self._constraints
