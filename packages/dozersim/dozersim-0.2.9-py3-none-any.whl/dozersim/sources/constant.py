from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from dozersim.path import Path
from dozersim.modelling import Model, Settings


@dataclass(slots=True)
class ConstantSettings(Settings):
    Target: str = None
    Magnitude: float = None


def evaluate_constant(paths: tuple[Path], constant: ConstantSettings, model: Model):
    path, = paths

    time = path.variables.time
    profile = np.full(time.shape, constant.Magnitude)
    path.variables.add(constant.Target, profile, model, f"{model.name}")


class Constant(Model):
    def __init__(self, name: str = 'constant', settings=ConstantSettings(), eval_fun=evaluate_constant):
        super().__init__(name=name, settings=settings, eval_fun=eval_fun)