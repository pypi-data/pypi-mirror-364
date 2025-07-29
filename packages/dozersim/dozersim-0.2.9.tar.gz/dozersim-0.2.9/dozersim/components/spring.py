from __future__ import annotations

from dataclasses import dataclass

from dozersim.path import Path
from dozersim.modelling import Model, Settings
from dozersim import constraints


@dataclass(slots=True)
class SpringSettings(Settings):
    stiffness: float = None
    max_torque: float = None


def evaluate_spring_deflection(paths: tuple[Path, Path], spring: SpringSettings, model: Model):
    path = paths[0]

    force = path.variables.effort
    deflection = force / spring.stiffness
    path.variables.add('displacement', deflection, model, "Spring deflection")

    model.constraints['peak_torque'].evaluate(model=model, path=path)


def evaluate_spring_force(paths: tuple[Path, Path], spring: SpringSettings, model: Model):
    path = paths[0]

    flows = path.variables.flows
    displacement1 = flows[-1].data[0]
    displacement2 = flows[-2].data[0]
    deflection = displacement2 - displacement1
    force = deflection * spring.stiffness
    path.variables.add('effort', force, model, "Spring force")

    model.constraints['peak_torque'].evaluate(model=model, path=path)


class Spring(Model):

    def __init__(self, name: str = 'spring', settings=SpringSettings(), eval_fun=evaluate_spring_deflection):
        super().__init__(name=name, settings=settings, eval_fun=eval_fun)
        self.add_constraint(constraints.PathConstraint(name='peak_torque', settings=settings, ub='max_torque',
                                                       statistic='absmax', target='effort'))
