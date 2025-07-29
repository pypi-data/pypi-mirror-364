from __future__ import annotations
from dataclasses import dataclass
import numpy as np

from dozersim import constraints
from dozersim.suppliers import MotorTable
from dozersim.path import Path
from dozersim.modelling import Settings
from dozersim.modelling import Model


@dataclass(slots=True)
class ElectricMotorSettings(Settings):
    name: str = None
    built: str = None
    windingResistance: float = None
    speedConstant: float = None
    maxSpeed: float = None
    peakPower: float = None
    ratedPower: float = None
    ratedCurrent: float = None
    peakCurrent: float = None
    windingVoltage: float = None
    rotorInertia: float = None
    mass: float = None
    motorLength: float = None
    motorDiameter: float = None

    @property
    def torqueConstant(self):
        return 1 / (self.speedConstant * np.pi / 30)

    @property
    def supplier_table(self):
        return MotorTable


def evaluate_electric_motor(paths: tuple[Path], motor: ElectricMotorSettings, model: Model):
    path = paths[0]

    path.check('rotational')

    # Get speed and
    speed = path.variables.velocity
    acceleration = path.variables.acceleration

    # Calculate and add rotor inertia moment
    if motor.rotorInertia:
        moment_inertia = motor.rotorInertia * acceleration
        path.variables.add('torque', moment_inertia, model, "Motor Inertia")

    # Calculate motor current and voltage
    torque = path.variables.torque
    motor_current = torque / motor.torqueConstant
    emf_voltage = speed * motor.torqueConstant
    resistance_voltage = motor.windingResistance * torque / motor.torqueConstant
    motor_voltage = emf_voltage + resistance_voltage
    motor_power = motor_voltage * motor_current

    path.transform(var_type='electrical', name="Motor input")
    path.variables.add('current', motor_current, model, "Motor Current")
    path.variables.add('voltage', emf_voltage, model, "EMF Voltage")
    path.variables.add('voltage', resistance_voltage, model, "Resistance Voltage")

    model.constraints['rated_current'].evaluate(model=model, path=path)
    model.constraints['peak_current'].evaluate(model=model, path=path)
    model.constraints['voltage'].evaluate(model=model, path=path)
    model.constraints['rated_power'].evaluate(model=model, path=path)
    model.constraints['peak_power'].evaluate(model=model, path=path)


class ElectricMotor(Model):
    def __init__(self, name: str = 'electricmotor', settings=ElectricMotorSettings(), eval_fun=evaluate_electric_motor):
        super().__init__(name=name, settings=settings, eval_fun=eval_fun)
        self.add_constraint(constraints.PathConstraint(name='rated_current', settings=settings, ub='ratedCurrent',
                                                       statistic='absmean', target='flow'))
        self.add_constraint(constraints.PathConstraint(name='peak_current', settings=settings, ub='peakCurrent',
                                                       statistic='absmax', target='flow'))
        self.add_constraint(constraints.PathConstraint(name='voltage', settings=settings, ub='windingVoltage',
                                                       statistic='absmax', target='effort'))
        self.add_constraint(constraints.PathConstraint(name='rated_power', settings=settings, ub='ratedPower',
                                                       statistic='absmean', target='power'))
        self.add_constraint(constraints.PathConstraint(name='peak_power', settings=settings, ub='peakPower',
                                                       statistic='absmax', target='power'))
