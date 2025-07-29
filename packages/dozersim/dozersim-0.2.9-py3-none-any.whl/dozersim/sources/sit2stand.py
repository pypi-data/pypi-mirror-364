from __future__ import annotations

import json
import os
from dataclasses import dataclass, field

import numpy as np
from scipy import interpolate

from dozersim.modelling import Model, Settings
from dozersim.variables import Flow
from dozersim.path import Path

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))


@dataclass(slots=True)
class Sit2StandDataSettings(Settings):
    Data: dict = None
    Joint: str = None
    SubjectBodyMass: float = None

    def __post_init__(self):
        with open(os.path.join(__location__, '../data/sit2stand_data.json')) as file_object:
            self.Data: dict = json.load(file_object)


def evaluate_sit2stand_data(paths: tuple[Path], sit2stand: Sit2StandDataSettings, model: Model):
    path, = paths

    path.check('rotational')
    old_time = sit2stand.Data["Time"]

    target = sit2stand.Joint
    torque_target = "Torque" + target
    angle_target = "Angle" + target
    speed_target = "Speed" + target
    torque_function = interpolate.interp1d(x=old_time, y=sit2stand.Data[torque_target], kind='cubic')
    angle_function = interpolate.interp1d(x=old_time, y=sit2stand.Data[angle_target], kind='cubic')
    speed_function = interpolate.interp1d(x=old_time, y=sit2stand.Data[speed_target], kind='cubic')

    new_time = path.variables.time
    torque = torque_function(new_time)
    angle = angle_function(new_time)
    speed = speed_function(new_time)
    acceleration = np.gradient(speed, new_time)

    data = {
        0: angle * np.pi / 180,
        1: speed * np.pi / 180,
        2: acceleration * np.pi / 180
    }
    flow = Flow(name=target, parent=model, data=data)
    path.variables.flows.append(flow)
    path.variables.add('torque', torque * sit2stand.SubjectBodyMass, model, torque_target)


class Sit2StandData(Model):

    def __init__(self, name: str = 'sit-to-stand data', settings=Sit2StandDataSettings(), eval_fun=evaluate_sit2stand_data):
        super().__init__(name=name, settings=settings, eval_fun=eval_fun)