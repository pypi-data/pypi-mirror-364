from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from dozersim.path import Path
from dozersim.modelling import Model, Settings


@dataclass(slots=True)
class TimeSourceSettings(Settings):
    TimeStart: float = None
    TimeEnd: float = None
    SampleTime: float = None


def evaluate_time_source(paths: tuple[Path], setting: TimeSourceSettings, model: Model):
    for path in paths:
        path.variables.add('time', np.arange(setting.TimeStart, setting.TimeEnd, setting.SampleTime), model, 'Time')


class TimeSource(Model):

    def __init__(self, name: str = 'time', settings: TimeSourceSettings = TimeSourceSettings(), eval_fun=evaluate_time_source):
        super().__init__(name=name, settings=settings, eval_fun=eval_fun)
