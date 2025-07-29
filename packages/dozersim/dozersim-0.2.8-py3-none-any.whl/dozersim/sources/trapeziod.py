from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from dozersim.path import Path
from dozersim.modelling import Model, Settings


@dataclass(slots=True)
class TrapezoidSettings(Settings):
    Target: str = None
    PeakValue: float = None
    TimeAtPeak: float = None
    TimeToPeak: float = None
    TimeStart: float = None


def evaluate_smooth_trapezoid(paths: tuple[Path], trapezoid: TrapezoidSettings, model: Model):
    path, = paths

    PeakValue = trapezoid.PeakValue
    TimeAtPeak = trapezoid.TimeAtPeak
    TimeToPeak = trapezoid.TimeToPeak
    TimeStart = trapezoid.TimeStart

    time = path.variables.time

    SampleTime = time[1] - time[0]

    if time[-1] < (TimeStart + TimeAtPeak + TimeToPeak * 2):
        raise Exception("Length of the Trapezoid is bigger than the length of time!!")

    tCurve = np.arange(0, TimeToPeak / 2, SampleTime)
    tFlat = np.arange(0, TimeAtPeak, SampleTime)
    Acceleration = 2 * (PeakValue) / TimeToPeak

    n0 = np.zeros(time[time < TimeStart].shape)
    n01a = Acceleration / TimeToPeak * tCurve ** 2
    n01b = PeakValue / 2 + Acceleration * tCurve - Acceleration / TimeToPeak * tCurve ** 2
    n12 = np.full(tFlat.shape, PeakValue)
    n23a = PeakValue - Acceleration / TimeToPeak * tCurve ** 2
    n23b = PeakValue / 2 - Acceleration * tCurve + Acceleration / TimeToPeak * tCurve ** 2

    profile = np.concatenate((n0, n01a, n01b, n12, n23a, n23b))
    n3 = np.zeros(time.size - profile.size)
    profile = np.concatenate((profile, n3))

    path.variables.add(trapezoid.Target, profile, model, "Trapezoid curve")


def evaluate_trapezoid(paths: tuple[Path], trapezoid: TrapezoidSettings, model: Model):
    path, = paths

    PeakValue = trapezoid.PeakValue
    TimeAtPeak = trapezoid.TimeAtPeak
    TimeToPeak = trapezoid.TimeToPeak
    TimeStart = trapezoid.TimeStart

    time = path.variables.time

    SampleTime = time[1] - time[0]

    if time[-1] < (TimeStart + TimeAtPeak + TimeToPeak * 2):
        raise Exception("Length of the Trapezoid is bigger than the length of time!!")

    tRamp = np.arange(0, TimeToPeak, SampleTime)
    tFlat = np.arange(0, TimeAtPeak, SampleTime)

    n0 = np.zeros(time[time < TimeStart].shape)
    n01 = PeakValue / TimeToPeak * tRamp
    n12 = np.full(tFlat.shape, PeakValue)
    n23 = PeakValue - PeakValue / TimeToPeak * tRamp

    profile = np.concatenate((n0, n01, n12, n23))
    n3 = np.zeros(time.size - profile.size)
    profile = np.concatenate((profile, n3))

    path.variables.add(trapezoid.Target, profile, model, "Trapezoidal profile")


class Trapezoid(Model):
    def __init__(self, name: str = 'trapezoid', settings=TrapezoidSettings(), eval_fun=evaluate_trapezoid):
        super().__init__(name=name, settings=settings, eval_fun=eval_fun)
