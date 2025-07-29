from __future__ import annotations
from dataclasses import dataclass
from dozersim.path import Path
from dozersim.modelling import Model, Settings
from dozersim import constraints
from dozersim.components import tools


@dataclass(slots=True)
class TransformerSettings(Settings):
    name: str = None
    ratio: float = None
    max_effort: float = None
    efficiency: float = None
    mass: float = None


def evaluate_transformer(paths: tuple[Path], transformer: TransformerSettings, model: Model):
    path = paths[0]

    effort_output = path.variables.efforts
    flow_output = path.variables.flow

    model.constraints['peak_effort'].evaluate(model=model, path=path)

    path.transform(var_type=path.variables.domain, name=f"{model.name} input")

    speed_input = flow_output * transformer.ratio

    path.variables.add('flow', speed_input, model, "Transformer input")

    for effort in effort_output:
        path.variables.add('effort', effort.data / transformer.ratio, model, effort.name)

    friction_torque = tools.calculate_friction_torque(effort=path.variables.effort,
                                                      power=path.variables.power,
                                                      efficiency=transformer.efficiency
                                                      )

    path.variables.add('effort', friction_torque, model, "Efficiency loss")


class Transformer(Model):
    def __init__(self, name: str = 'transformer', settings=TransformerSettings(), eval_fun=evaluate_transformer):
        super().__init__(name=name, settings=settings, eval_fun=eval_fun)
        self.add_constraint(constraints.PathConstraint(name='peak_effort', settings=settings, ub='max_effort',
                                                       statistic='absmax', target='effort'))


