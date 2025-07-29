from __future__ import annotations
from dataclasses import dataclass
from dozersim.path import Path
from dozersim.modelling import Model, Settings
from dozersim import constraints
from dozersim.components import tools


@dataclass(slots=True)
class GearboxSettings(Settings):
    name: str = None
    ratio: float = None
    max_torque: float = None
    efficiency: float = None
    mass: float = None


def evaluate_gearbox(paths: tuple[Path], gearbox: GearboxSettings, model: Model):
    path = paths[0]

    path.check('rotational')

    torques_output = path.variables.efforts
    torque_output_total = path.variables.torque
    speed_output = path.variables.velocity

    model.constraints['peak_torque'].evaluate(model=model, path=path)

    path.transform(var_type='rotational', name=f"{model.name} input")

    speed_input = speed_output * gearbox.ratio

    path.variables.add('velocity', speed_input, model, "Gearbox input")

    for TorqueOutput in torques_output:
        path.variables.add('torque', TorqueOutput.data / gearbox.ratio, model, TorqueOutput.name)

    friction_torque = tools.calculate_friction_torque(effort=path.variables.effort,
                                                      power=path.variables.power,
                                                      efficiency=gearbox.efficiency
                                                      )

    path.variables.add('torque', friction_torque, model, "Gearbox friction")


class Gearbox(Model):
    def __init__(self, name: str = 'gearbox', settings=GearboxSettings(), eval_fun=evaluate_gearbox):
        super().__init__(name=name, settings=settings, eval_fun=eval_fun)
        self.add_constraint(constraints.PathConstraint(name='peak_torque', settings=settings, ub='max_torque',
                                                       statistic='absmax', target='effort'))


