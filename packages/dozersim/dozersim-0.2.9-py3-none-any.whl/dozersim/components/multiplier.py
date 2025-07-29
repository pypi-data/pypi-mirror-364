
from __future__ import annotations
from dataclasses import dataclass, field
import numpy as np
from dozersim.path import Path
from dozersim.modelling import Model, Settings
from dozersim.results import Load


@dataclass(slots=True)
class MultiplierSettings(Settings):
    number: int = None # Number of identical items
    target: str = None # e.g. 'effort' or 'flow'


def evaluate_multiplier(paths: tuple[Path], multiplier: MultiplierSettings, model: Model):
    """
        Multipliers simulates multiple identical items
        multipliers are independent of the type of variable they are applied to
        and can be used to multiply the results of a path by a constant factor.

    """
    path, = paths

    gains = {'flow': 1, 'effort': 1}
    values = {'flow': path.variables.flow, 'effort': path.variables.effort}
    try:
        gains[multiplier.target] = multiplier.number
    except KeyError:
        raise ValueError(f"Unknown multiplier target: {multiplier.target}. Available targets are: {list(gains.keys())}")
    
    path.transform(var_type=path.variables.domain, name=f'{multiplier.number} items in {multiplier.target}')

    for target in gains.keys():
        path.variables.add(target=target,
            values=values[target]*gains[target],
            parent=model,
            name=f'Multiplier {multiplier.target}')



class Multiplier(Model):
    def __init__(self, name: str = 'multiplier', settings=MultiplierSettings(), eval_fun=evaluate_multiplier):
        super().__init__(name=name, settings=settings, eval_fun=eval_fun)
