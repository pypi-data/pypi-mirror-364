"""
Module: settings_management

This module defines the `Model` class, which provides a framework for managing
settings and constraints for a simulation. It allows dynamic addition and retrieval
of settings and constraints and defines a customizable evaluation function.

Classes
-------
Model
    Abstract settings class for managing settings and constraints in a simulation.

Attributes
----------
_constraints : dict[str, constraints.Constraint]
    Dictionary of constraints mapped by their names.
eval_fun : callable
    Evaluation function used for custom logic.

Usage Example
-------------
>>> from dozersim.settings import Settings
>>> part = Settings()
>>> part.set_setting("max_speed", 100)
>>> print(part.get_setting("max_speed"))
100
"""
from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field


@dataclass
class Settings(ABC):
    """
    Abstract settings class for managing simulation part and constraints.

    Attributes
    ----------
    _constraints : dict[str, constraints.Constraint]
        Dictionary of constraints, where keys are constraint names and values
        are `Constraint` objects.
    eval_fun : callable
        Function for custom evaluation logic.
    """

    def set_setting(self, keyword: str, value):
        """
        Dynamically sets a setting attribute.

        Parameters
        ----------
        keyword : str
            Name of the setting to set.
        value : Any
            Value to assign to the setting.
        """
        setattr(self, keyword, value)

    def get_setting(self, keyword: str):
        """
        Retrieves the value of a specified setting attribute.

        Parameters
        ----------
        keyword : str
            Name of the setting to retrieve.

        Returns
        -------
        Any
            Value of the specified setting.

        Raises
        ------
        AttributeError
            If the specified setting does not exist.
        """
        try:
            return getattr(self, keyword)
        except AttributeError as e:
            raise AttributeError(e)

    @property
    def supplier_table(self):
        """
        Placeholder for a supplier table. Can be overridden in subclasses.

        Returns
        -------
        None
        """
        return None
