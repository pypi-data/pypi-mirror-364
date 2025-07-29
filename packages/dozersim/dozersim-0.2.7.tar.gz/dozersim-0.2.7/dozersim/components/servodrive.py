from __future__ import annotations
from dataclasses import dataclass
import numpy as np

from dozersim.path import Path
from dozersim.modelling import Model, Settings
from dozersim import constraints


@dataclass(slots=True)
class ServoDriveSettings(Settings):
    name: str = None
    ContinuousCurrent: float = None
    PeakCurrent: float = None
    MaxVoltage: float = None
    SwitchingFrequency: float = None
    SupplyVoltage: float = None
    BusUtilizationFactor: float = np.sqrt(3) / 2


def evaluate_servo_drive(paths: tuple[Path], servo: ServoDriveSettings, model: Model):
    path = paths[0]

    path.check('electrical')

    motor_power = path.variables.power

    supply_voltage = np.full(np.array(motor_power).shape, servo.SupplyVoltage)
    supply_current = motor_power / supply_voltage
    utilization_loss = servo.SupplyVoltage*servo.BusUtilizationFactor

    model.constraints['rated_current'].evaluate(model=model, path=path)
    model.constraints['peak_current'].evaluate(model=model, path=path)
    model.constraints['max_voltage'].evaluate(model=model, path=path)

    path.transform(var_type='electrical', name="Supply variables")
    path.variables.add('effort', supply_voltage, model, 'Supply Voltage')
    path.variables.add('current', supply_current, model, 'Supply Current')


class ServoDrive(Model):

    def __init__(self, name: str = 'servodrive', settings=ServoDriveSettings(), eval_fun=evaluate_servo_drive):
        super().__init__(name=name, settings=settings, eval_fun=eval_fun)
        self.add_constraint(constraints.PathConstraint(name='rated_current', settings=settings, ub='ContinuousCurrent',
                                                       statistic='absmean', target='flow'))
        self.add_constraint(constraints.PathConstraint(name='peak_current', settings=settings, ub='PeakCurrent',
                                                       statistic='absmax', target='flow'))
        self.add_constraint(constraints.PathConstraint(name='max_voltage', settings=settings, ub='MaxVoltage',
                                                       statistic='absmax', target='effort'))
