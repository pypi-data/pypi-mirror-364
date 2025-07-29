from __future__ import annotations
from dataclasses import dataclass, field
from dozersim.path import Path
from dozersim.modelling import Model, Settings


@dataclass(slots=True)
class InertiaSettings(Settings):
    name: str = None
    inertia: float = None


def evaluate_inertia(paths: tuple[Path], inertia: InertiaSettings, model: Model):
    path = paths[0]

    path.check('rotational')

    acceleration = path.variables.acceleration

    # Calculate and add rotor inertia moment
    moment_inertia = inertia.inertia * acceleration
    path.variables.add('effort', moment_inertia, model, f'{inertia.name}')
    # paths.variable.add_effort(moment_intertia, model, "Generic InertiaSettings")


class Inertia(Model):
    def __init__(self, name: str = 'inertia', settings=InertiaSettings(), eval_fun=evaluate_inertia):
        super().__init__(name=name, settings=settings, eval_fun=eval_fun)

