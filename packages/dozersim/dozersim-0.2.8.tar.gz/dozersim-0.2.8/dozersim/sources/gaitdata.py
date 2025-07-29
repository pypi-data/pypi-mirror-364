from __future__ import annotations

import json
import os
from dataclasses import dataclass, field

import numpy as np

from dozersim.path import Path
from dozersim.modelling import Model, Settings

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))




@dataclass(slots=True)
class GaitDataSettings(Settings):
    Data: dict = None
    SubjectBodyMass: float = None
    Joint: str = None
    Speed: str = None

    def __post_init__(self):
        with open(os.path.join(__location__, '../data/gait_data.json')) as file_object:
            self.Data: dict = json.load(file_object)


def evaluate_gait_data(paths: list[Path], gaitdata: GaitDataSettings, model: Model):
    path, = paths

    path.check('rotational')
    time = gaitdata.Data["TimeNormal"]
    time_new = path.variables.time
    target = gaitdata.Joint + gaitdata.Speed
    torque_target = "Torque" + target
    angle_target = "Angle" + target
    speed_target = "Speed" + target
    torque = np.interp(x=time_new, xp=time, fp=gaitdata.Data[torque_target])
    angle = np.interp(x=time_new, xp=time, fp=gaitdata.Data[angle_target])
    speed = np.interp(x=time_new, xp=time, fp=gaitdata.Data[speed_target])
    acceleration = np.gradient(speed, time_new)
    '''
    data = {
            0: angle,
            1: speed,
            2: acceleration
    }
    '''
    # flow = Flow(name=_target, parent=model, data=data)
    # paths.variables.flows.append(flow)
    path.variables.add('velocity', values=speed, parent=model, name=torque_target)
    path.variables.add('torque', torque * gaitdata.SubjectBodyMass, model, torque_target)


class GaitData(Model):

    def __init__(self, name: str = 'gait data', settings=GaitDataSettings, eval_fun=evaluate_gait_data):
        super().__init__(name=name, settings=settings, eval_fun=eval_fun)
